#!/usr/bin/env python3
# ruff: noqa: PLR0915,S603,S607,S108
"""Forward Motion scanner.

Collects the latest message state for all configured fleet threads.
Supports:
- Telegram forum topics (operator topics and bot DM subtopics) via MTProto
- Flat chats (general bot DMs and support groups) via tgcli

This script is read-only. It does not update SQLite state.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

from telethon import TelegramClient
from telethon.tl.functions.messages import GetRepliesRequest

WORKFLOW_DIR = Path(__file__).resolve().parents[1]
RULES_PATH = WORKFLOW_DIR / "rules.md"
TGCLI_CONFIG = Path("~/.tgcli/config.json").expanduser()
OPENCLAW_CONFIG = Path("~/.openclaw/openclaw.json").expanduser()
DEFAULT_SESSION = str(Path("~/.tgcli/telethon-session").expanduser())
TGCLI_BIN = shutil.which("tgcli") or "tgcli"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _extract_structured_rules(text: str) -> dict[str, Any] | None:
    if yaml is None:
        return None
    blocks = re.findall(r"```yaml\n(.*?)\n```", text, flags=re.DOTALL)
    for block in blocks:
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError:
            data = None
        if isinstance(data, dict) and any(k in data for k in ["account", "fleet"]):
            return data
    return None


def _legacy_sections(
    text: str,
) -> tuple[dict[str, Any], list[str], list[str], list[str], list[str]]:
    account: dict[str, Any] = {}
    topic_lines: list[str] = []
    bot_lines: list[str] = []
    group_lines: list[str] = []
    vip_lines: list[str] = []

    human_match = re.search(r"human:\s*(.*?)\s*\((\d+)\)", text)
    if human_match:
        account["human_name"] = human_match.group(1).strip()
        account["human_id"] = int(human_match.group(2))

    alert_match = re.search(r"alert_topic:\s*(\d+)", text)
    if alert_match:
        account["alert_topic"] = int(alert_match.group(1))

    current: list[str] | None = None
    vip_section = False
    for line in text.splitlines():
        if "### Cora DM Topics" in line:
            current = topic_lines
            vip_section = False
            continue
        if "### Bot DMs" in line:
            current = bot_lines
            vip_section = False
            continue
        if "### Support Groups" in line:
            current = group_lines
            vip_section = False
            continue
        if line.strip().startswith("## VIP"):
            vip_section = True
            current = None
            continue
        if line.startswith("##") and "Fleet Map" not in line:
            current = None
            if not line.strip().startswith("## VIP"):
                vip_section = False

        if current is not None and line.startswith("|"):
            current.append(line)
        if vip_section and line.strip().startswith("-"):
            vip_lines.append(line)

    return account, topic_lines, bot_lines, group_lines, vip_lines


def _parse_topic_lines(lines: list[str], human_id: int | None) -> list[dict[str, Any]]:
    topics: list[dict[str, Any]] = []
    for line in lines:
        if any(line.startswith(prefix) for prefix in ["| Thread", "|-----", "|---"]):
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        try:
            if len(parts) >= 3:
                topics.append(
                    {
                        "chat_id": human_id,
                        "topic_id": int(parts[0]),
                        "name": parts[1],
                        "scope": parts[2],
                    }
                )
        except (ValueError, IndexError):
            continue
    return topics


def _parse_bot_lines(lines: list[str]) -> list[dict[str, Any]]:
    bots: list[dict[str, Any]] = []
    for line in lines:
        if any(line.startswith(prefix) for prefix in ["| Bot |", "|-----", "|---"]):
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        try:
            if len(parts) < 3:
                continue
            subtopics: list[dict[str, Any]] = []
            if parts[2] != "(flat)":
                for raw_item in parts[2].split(","):
                    cleaned = raw_item.strip()
                    if "=" not in cleaned:
                        continue
                    sid, sname = cleaned.split("=", 1)
                    subtopics.append({"topic_id": int(sid), "name": sname.strip()})
            bots.append(
                {
                    "peer_id": int(parts[1]),
                    "name": parts[0],
                    "scope": "fleet",
                    "subtopics": subtopics,
                }
            )
        except (ValueError, IndexError):
            continue
    return bots


def _parse_group_lines(lines: list[str]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for line in lines:
        if any(line.startswith(prefix) for prefix in ["| Group |", "|-----", "|---"]):
            continue
        parts = [p.strip() for p in line.split("|")[1:-1]]
        try:
            if len(parts) >= 2:
                groups.append(
                    {
                        "chat_id": int(parts[1]),
                        "name": parts[0],
                        "scope": "fleet",
                    }
                )
        except (ValueError, IndexError):
            continue
    return groups


def _parse_legacy_rules(text: str) -> dict[str, Any]:
    account, topic_lines, bot_lines, group_lines, vip_lines = _legacy_sections(text)
    vips = [line.split("-", 1)[1].strip() for line in vip_lines]
    fleet = {
        "topics": _parse_topic_lines(topic_lines, account.get("human_id")),
        "bots": _parse_bot_lines(bot_lines),
        "groups": _parse_group_lines(group_lines),
    }
    cleanup = {"enabled": True, "min_age_hours": 2}
    return {"account": account, "fleet": fleet, "vips": vips, "cleanup": cleanup}


def load_rules(path: Path) -> dict[str, Any]:
    text = path.read_text()
    structured = _extract_structured_rules(text)
    if structured:
        return structured
    return _parse_legacy_rules(text)


def tgcli_latest(peer_id: int, limit: int = 3) -> dict[str, Any] | None:
    proc = subprocess.run(  # noqa: S603
        [TGCLI_BIN, "msg", "ls", str(peer_id), "--limit", str(limit), "--json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    msgs = json.loads(proc.stdout)
    if not msgs:
        return None
    msg = msgs[0]
    return {
        "msg_id": msg.get("msg_id"),
        "msg_at": (msg.get("timestamp") or "")[:19],
        "sender": msg.get("sender_name") or "",
        "from_me": msg.get("from_me", False),
        "preview": (msg.get("text") or "")[:160],
    }


async def _make_client(cfg: dict[str, Any], session: str) -> TelegramClient:
    client = TelegramClient(
        session,
        cfg["app_id"],
        cfg["app_hash"],
        receive_updates=False,
    )
    await client.connect()
    return client


async def _entity_map(client: TelegramClient) -> dict[int, Any]:
    entities: dict[int, Any] = {}
    async for dialog in client.iter_dialogs():
        eid = getattr(dialog.entity, "id", None)
        if eid:
            entities[eid] = dialog.entity
    return entities


async def _topic_latest(
    client: TelegramClient,
    entity: Any,
    topic_id: int,
    human_id: int,
    bot_id: int,
    default_sender: str,
) -> dict[str, Any] | None:
    try:
        replies = await client(
            GetRepliesRequest(
                peer=entity,
                msg_id=topic_id,
                offset_id=0,
                offset_date=0,
                add_offset=0,
                limit=1,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)[:160]}

    messages = getattr(replies, "messages", [])
    if not messages:
        return None
    msg = messages[0]
    from_id = getattr(msg, "from_id", None)
    uid = getattr(from_id, "user_id", None) if from_id else None
    if uid == human_id:
        sender = "human"
    elif uid == bot_id:
        sender = "assistant"
    elif uid:
        sender = str(uid)
    else:
        sender = default_sender
    return {
        "msg_id": getattr(msg, "id", None),
        "msg_at": (
            msg.date.strftime("%Y-%m-%dT%H:%M:%S") if getattr(msg, "date", None) else ""
        ),
        "sender": sender,
        "preview": (getattr(msg, "message", "") or "")[:160],
    }


async def scan(  # noqa: PLR0915
    session: str,
    rules_path: Path,
) -> dict[str, Any]:
    rules = load_rules(rules_path)
    tgcli_cfg = _load_json(TGCLI_CONFIG)
    oc_cfg = _load_json(OPENCLAW_CONFIG)
    bot_id = int(oc_cfg["channels"]["telegram"]["botToken"].split(":")[0])
    human_id = int(rules["account"]["human_id"])

    results: dict[str, Any] = {}

    client = await _make_client(tgcli_cfg, session)
    try:
        if not await client.is_user_authorized():
            raise RuntimeError("Telegram client session is not authorized")
        entity_lookup = await _entity_map(client)
        operator_entity = entity_lookup.get(bot_id)
        for topic in rules.get("fleet", {}).get("topics", []):
            key = f"{topic['chat_id']}:{topic['topic_id']}"
            scope = topic.get("scope", "fleet")
            if scope in {"skip", "output-only"}:
                results[key] = {
                    "skipped": True,
                    "thread_name": topic["name"],
                    "scope": scope,
                }
                continue
            if not operator_entity:
                results[key] = {
                    "error": "operator bot entity not found",
                    "thread_name": topic["name"],
                    "scope": scope,
                }
                continue
            info = await _topic_latest(
                client,
                operator_entity,
                int(topic["topic_id"]),
                human_id,
                bot_id,
                "assistant",
            )
            if info:
                info["thread_name"] = topic["name"]
                info["scope"] = scope
                results[key] = info
            else:
                results[key] = {
                    "msg_id": None,
                    "thread_name": topic["name"],
                    "scope": scope,
                }
    finally:
        await client.disconnect()

    for bot in rules.get("fleet", {}).get("bots", []):
        peer_id = int(bot["peer_id"])
        client = await _make_client(tgcli_cfg, session)
        try:
            entity_lookup = await _entity_map(client)
            entity = entity_lookup.get(peer_id)
            for subtopic in bot.get("subtopics", []) or []:
                key = f"{peer_id}:{subtopic['topic_id']}"
                if not entity:
                    results[key] = {
                        "error": "bot entity not found",
                        "thread_name": f"{bot['name']}/{subtopic['name']}",
                        "scope": bot.get("scope", "fleet"),
                    }
                    continue
                info = await _topic_latest(
                    client,
                    entity,
                    int(subtopic["topic_id"]),
                    human_id,
                    bot_id,
                    bot["name"],
                )
                if info:
                    info["thread_name"] = f"{bot['name']}/{subtopic['name']}"
                    info["scope"] = bot.get("scope", "fleet")
                    results[key] = info
                else:
                    results[key] = {
                        "msg_id": None,
                        "thread_name": f"{bot['name']}/{subtopic['name']}",
                        "scope": bot.get("scope", "fleet"),
                    }
        finally:
            await client.disconnect()

        general = tgcli_latest(peer_id)
        general_key = str(peer_id)
        if general:
            general["thread_name"] = f"{bot['name']} (general)"
            general["scope"] = bot.get("scope", "fleet")
            results[general_key] = general
        else:
            results[general_key] = {
                "error": "tgcli returned nothing",
                "thread_name": f"{bot['name']} (general)",
                "scope": bot.get("scope", "fleet"),
            }

    for group in rules.get("fleet", {}).get("groups", []):
        key = str(group["chat_id"])
        info = tgcli_latest(int(group["chat_id"]))
        if info:
            info["thread_name"] = group["name"]
            info["scope"] = group.get("scope", "fleet")
            results[key] = info
        else:
            results[key] = {
                "error": "tgcli returned nothing",
                "thread_name": group["name"],
                "scope": group.get("scope", "fleet"),
            }

    total = len(results)
    skipped = sum(1 for value in results.values() if value.get("skipped"))
    errors = [
        f"{value['thread_name']}: {value['error']}"
        for value in results.values()
        if value.get("error")
    ]
    errored = len(errors)
    active = total - skipped - errored

    return {
        "summary": {
            "total_threads": total,
            "active": active,
            "skipped": skipped,
            "errored": errored,
            "errors": errors,
            "scanned_at": datetime.now(UTC).isoformat(),
        },
        "threads": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", type=Path, default=RULES_PATH)
    parser.add_argument("--session", default=DEFAULT_SESSION)
    args = parser.parse_args()
    result = asyncio.run(scan(session=args.session, rules_path=args.rules))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

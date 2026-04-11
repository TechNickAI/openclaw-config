#!/usr/bin/env python3
"""Discover all Telegram forum topics for a list of peers.

Uses the Telegram Client API (MTProto) via Telethon to call
GetForumTopicsRequest -- something the Bot API cannot do.

Requires:
- tgcli authenticated (session in ~/.tgcli/)
- Telethon installed: pip install telethon
- Session converted: python3 convert-session.py

Usage:
    python3 discover-topics.py [--peers 123,456,...] [--all]
    python3 discover-topics.py --all --json
    python3 discover-topics.py --all --markdown
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.functions.messages import GetForumTopicsRequest

DEFAULT_SESSION = "/tmp/tg-session"  # noqa: S108


def load_config() -> dict:
    cfg_path = Path("~/.tgcli/config.json").expanduser()
    return json.loads(cfg_path.read_text())


def _output_text(results: dict) -> None:
    for pid, info in sorted(results.items(), key=lambda x: x[1].get("name", "")):
        name = info.get("name", pid)
        topics = info.get("topics", [])
        error = info.get("error", "")
        print(f"{name} ({pid}):")
        if error:
            print(f"  error: {error}")
        elif topics:
            for t in topics:
                print(f"  {t['id']}: {t['name']}")
        else:
            print("  (no topics)")


def _output_markdown(results: dict) -> None:
    print("# Telegram Thread/Topic Map")
    print("*Auto-generated via Client API*\n")
    for pid, info in sorted(results.items(), key=lambda x: x[1].get("name", "")):
        name = info.get("name", pid)
        topics = info.get("topics", [])
        error = info.get("error", "")
        print(f"## {name} ({pid})")
        if error:
            print(f"Error: {error}\n")
        elif topics:
            print("| Thread ID | Topic |")
            print("|-----------|-------|")
            for t in topics:
                print(f"| {t['id']} | {t['name']} |")
            print()
        else:
            print("(no topics)\n")


async def _scan_peer(client, entity, dialog_name: str) -> dict:
    """Try to get forum topics for a single peer."""
    try:
        result = await client(
            GetForumTopicsRequest(
                peer=entity,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100,
                q="",
            )
        )
        topics = [
            {"id": t.id, "name": t.title}
            for t in sorted(result.topics, key=lambda x: x.id)
        ]
        return {
            "name": dialog_name,
            "peer_id": getattr(entity, "id", 0),
            "topics": topics,
        }
    except Exception as exc:  # noqa: BLE001
        logging.debug("Not a forum: %s (%s)", dialog_name, exc)
        return {}


async def discover(
    peers: list[int] | None = None,
    scan_all: bool = False,
    output_format: str = "text",
    session_path: str = DEFAULT_SESSION,
) -> None:
    cfg = load_config()
    sess = Path(f"{session_path}.session")
    if not sess.exists():
        print(
            "Session not found. Run convert-session.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = TelegramClient(session_path, cfg["app_id"], cfg["app_hash"])
    await client.connect()

    if not await client.is_user_authorized():
        print(
            "Not authorized. Re-run tgcli login + convert-session.py.",
            file=sys.stderr,
        )
        await client.disconnect()
        sys.exit(1)

    results: dict[str, dict] = {}

    if scan_all:
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            eid = getattr(entity, "id", None)
            if not eid or (peers and eid not in peers):
                continue
            info = await _scan_peer(client, entity, dialog.name)
            if info and info.get("topics"):
                results[str(eid)] = info
    else:
        for peer_id in peers or []:
            entity = None
            async for dialog in client.iter_dialogs():
                if getattr(dialog.entity, "id", None) == peer_id:
                    entity = dialog.entity
                    break
            if not entity:
                results[str(peer_id)] = {"error": "not found"}
                continue
            info = await _scan_peer(
                client, entity, getattr(entity, "first_name", str(peer_id))
            )
            results[str(peer_id)] = info or {"error": "not a forum"}

    await client.disconnect()

    if output_format == "json":
        print(json.dumps(results, indent=2))
    elif output_format == "markdown":
        _output_markdown(results)
    else:
        _output_text(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Discover Telegram forum topics",
    )
    parser.add_argument("--peers", help="Comma-separated peer IDs")
    parser.add_argument("--all", action="store_true", help="Scan all dialogs")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--markdown", action="store_true", help="Markdown output")
    args = parser.parse_args()

    peer_list = [int(p) for p in args.peers.split(",")] if args.peers else None
    fmt = "json" if args.json else ("markdown" if args.markdown else "text")
    asyncio.run(discover(peers=peer_list, scan_all=args.all, output_format=fmt))

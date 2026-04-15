#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import gzip
import json
import os
from pathlib import Path
import shutil
import socket
import tempfile
from typing import Any
from collections.abc import Iterable

KEEP_COUNT_DEFAULT = 500
KEEP_DAYS_DEFAULT = 14
ARCHIVE_VERSION = 2


def build_protect_prefixes(agent_id: str) -> tuple[str, ...]:
    """Build protection prefixes dynamically based on agent_id."""
    return (
        f"agent:{agent_id}:main",
        f"agent:{agent_id}:telegram:",
        f"agent:{agent_id}:slack:",
        f"agent:{agent_id}:imessage:",
        f"agent:{agent_id}:whatsapp:",
        f"agent:{agent_id}:discord:",
    )


class ArchiveError(Exception):
    pass


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def iso(ts_ms: int | None) -> str | None:
    if not ts_ms:
        return None
    return dt.datetime.fromtimestamp(ts_ms / 1000, tz=dt.UTC).isoformat()


_KEY_KIND_MARKERS: tuple[tuple[str, str], ...] = (
    (":subagent:", "subagent"),
    (":cron:", "cron"),
    (":hook:", "hook"),
    (":telegram:", "telegram"),
    (":slack:", "slack"),
    (":discord:", "discord"),
    (":whatsapp:", "whatsapp"),
    (":imessage:", "imessage"),
)


def classify_key(key: str) -> str:
    for marker, kind in _KEY_KIND_MARKERS:
        if marker in key:
            return kind
    return "other"


def should_protect(key: str, protect_prefixes: Iterable[str]) -> bool:
    return any(key.startswith(prefix) for prefix in protect_prefixes)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def atomic_json_write(path: Path, obj: Any) -> None:
    ensure_parent(path)
    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w") as f:
            # Pretty-print all JSON files with consistent formatting
            indent = 2 if path.suffix == ".json" else None
            json.dump(obj, f, indent=indent)
            f.flush()
            os.fsync(f.fileno())
        tmp_path.chmod(0o600)
        tmp_path.replace(path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def relative_symlink(target: Path, link_path: Path) -> None:
    ensure_parent(link_path)
    if link_path.exists() or link_path.is_symlink():
        link_path.unlink()
    rel = os.path.relpath(target, start=link_path.parent)
    link_path.symlink_to(rel)


def load_store(store_path: Path) -> dict[str, Any]:
    with store_path.open() as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ArchiveError(f"Session store is not an object map: {store_path}")
    return data


def collect_candidates(
    store: dict[str, Any],
    keep_count: int,
    keep_days: int,
    protect_prefixes: tuple[str, ...],
) -> tuple[list[tuple[str, dict[str, Any]]], list[tuple[str, dict[str, Any]]]]:
    items = sorted(
        store.items(), key=lambda kv: kv[1].get("updatedAt", 0), reverse=True
    )
    kept: list[tuple[str, dict[str, Any]]] = []
    archived: list[tuple[str, dict[str, Any]]] = []
    cutoff_ms = int((now_utc() - dt.timedelta(days=keep_days)).timestamp() * 1000)

    for idx, (key, entry) in enumerate(items):
        kind = classify_key(key)
        updated_at = entry.get("updatedAt", 0)
        protected = should_protect(key, protect_prefixes)

        if protected or idx < keep_count:
            kept.append((key, entry))
            continue

        if kind in {"subagent", "cron", "hook"}:
            archived.append((key, entry))
            continue

        if updated_at and updated_at < cutoff_ms:
            archived.append((key, entry))
            continue

        kept.append((key, entry))

    return kept, archived


def archive_run_paths(archive_root: Path, agent_id: str) -> tuple[Path, Path]:
    stamp = now_utc().strftime("%Y/%m/%d/%H%M%S")
    base = archive_root / agent_id / stamp
    final_dir = base
    temp_dir = archive_root / agent_id / ".tmp" / f"{stamp}-{os.getpid()}"
    return temp_dir, final_dir


def prepare_manifest(key: str, entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "archiveVersion": ARCHIVE_VERSION,
        "sessionKey": key,
        "kind": classify_key(key),
        "updatedAt": entry.get("updatedAt"),
        "updatedAtIso": iso(entry.get("updatedAt")),
        "sessionId": entry.get("sessionId"),
        "sessionFile": entry.get("sessionFile"),
        "entry": entry,
    }


def archive_entry(
    temp_dir: Path, key: str, entry: dict[str, Any]
) -> tuple[dict[str, Any], Path | None]:
    entries_dir = temp_dir / "entries"
    transcripts_dir = temp_dir / "transcripts"
    entries_dir.mkdir(parents=True, exist_ok=True)
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    safe_name = key.replace("/", "_").replace(":", "__")
    manifest = prepare_manifest(key, entry)
    transcript_to_delete: Path | None = None

    transcript_path = entry.get("sessionFile")
    if transcript_path:
        src = Path(transcript_path)
        manifest["sourceTranscriptExists"] = src.exists()
        if src.exists() and src.is_file():
            dst = transcripts_dir / (src.name + ".gz")
            with src.open("rb") as fin, gzip.open(dst, "wb") as fout:
                shutil.copyfileobj(fin, fout)
            transcript_to_delete = src
            manifest["archivedTranscript"] = str(dst)
        else:
            manifest["archivedTranscript"] = None
    else:
        manifest["archivedTranscript"] = None

    entry_path = entries_dir / f"{safe_name}.json"
    entry_path.write_text(json.dumps(manifest, indent=2))
    return manifest, transcript_to_delete


def append_archive_index(
    archive_root: Path, agent_id: str, summary: dict[str, Any]
) -> None:
    index_path = archive_root / agent_id / "archive-index.jsonl"
    ensure_parent(index_path)
    with index_path.open("a") as f:
        f.write(json.dumps(summary) + "\n")


def delete_sources(paths: Iterable[Path]) -> list[str]:
    failures: list[str] = []
    for path in paths:
        try:
            if path.exists():
                path.unlink()
        except Exception as exc:
            failures.append(f"{path}: {exc}")
    return failures


def run_archive(
    state_dir: Path,
    agent_id: str,
    keep_count: int,
    keep_days: int,
    archive_root: Path,
    dry_run: bool,
) -> dict[str, Any]:
    sessions_dir = state_dir / "agents" / agent_id / "sessions"
    store_path = sessions_dir / "sessions.json"
    latest_link = archive_root / agent_id / "latest"
    protect_prefixes = build_protect_prefixes(agent_id)
    store = load_store(store_path)
    kept, archived = collect_candidates(store, keep_count, keep_days, protect_prefixes)

    by_kind: dict[str, int] = {}
    for key, _entry in archived:
        kind = classify_key(key)
        by_kind[kind] = by_kind.get(kind, 0) + 1

    summary: dict[str, Any] = {
        "archiveVersion": ARCHIVE_VERSION,
        "host": socket.gethostname(),
        "agentId": agent_id,
        "storePath": str(store_path),
        "archiveRoot": str(archive_root / agent_id),
        "beforeCount": len(store),
        "keepCount": len(kept),
        "archiveCount": len(archived),
        "keepCountLimit": keep_count,
        "keepDays": keep_days,
        "byKind": by_kind,
        "dryRun": dry_run,
        "ranAt": now_utc().isoformat(),
    }

    if dry_run or not archived:
        summary["runDir"] = None
        summary["deletedSourceTranscripts"] = 0
        summary["deleteFailures"] = []
        return summary

    temp_dir, final_dir = archive_run_paths(archive_root, agent_id)
    temp_dir.mkdir(parents=True, exist_ok=True)

    manifests: list[dict[str, Any]] = []
    sources_to_delete: list[Path] = []
    for key, entry in archived:
        manifest, source = archive_entry(temp_dir, key, entry)
        manifests.append(manifest)
        if source:
            sources_to_delete.append(source)

    atomic_json_write(temp_dir / "summary.json", summary)

    # Finalize archive directory BEFORE pruning sessions.json to avoid data loss window
    ensure_parent(final_dir)
    if final_dir.exists():
        raise ArchiveError(f"Archive destination already exists: {final_dir}")
    temp_dir.rename(final_dir)

    # Fix archivedTranscript paths in both manifest.jsonl AND individual entry files
    temp_prefix = str(temp_dir)
    final_prefix = str(final_dir)
    for m in manifests:
        if m.get("archivedTranscript") and str(m["archivedTranscript"]).startswith(
            temp_prefix
        ):
            m["archivedTranscript"] = str(m["archivedTranscript"]).replace(
                temp_prefix, final_prefix, 1
            )

    # Write updated manifest.jsonl
    (final_dir / "manifest.jsonl").write_text(
        "".join(json.dumps(m) + "\n" for m in manifests)
    )

    # Rewrite individual entry files with corrected paths
    entries_dir = final_dir / "entries"
    for m in manifests:
        key = m["sessionKey"]
        safe_name = key.replace("/", "_").replace(":", "__")
        entry_path = entries_dir / f"{safe_name}.json"
        entry_path.write_text(json.dumps(m, indent=2))

    # Now that archive is safely finalized, prune sessions.json
    new_store = {k: v for k, v in kept}
    atomic_json_write(store_path, new_store)

    delete_failures = delete_sources(sources_to_delete)
    summary["runDir"] = str(final_dir)
    summary["deletedSourceTranscripts"] = len(sources_to_delete) - len(delete_failures)
    summary["deleteFailures"] = delete_failures

    atomic_json_write(final_dir / "summary.json", summary)
    append_archive_index(archive_root, agent_id, summary)
    relative_symlink(final_dir, latest_link)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Archive stale OpenClaw sessions while keeping a bounded live working set"
        )
    )
    parser.add_argument("--state-dir", default=str(Path.home() / ".openclaw"))
    parser.add_argument("--agent-id", default="main")
    parser.add_argument("--archive-root", default=None)
    parser.add_argument("--keep-count", type=int, default=KEEP_COUNT_DEFAULT)
    parser.add_argument("--keep-days", type=int, default=KEEP_DAYS_DEFAULT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    state_dir = Path(args.state_dir).expanduser().resolve()
    archive_root = (
        Path(args.archive_root).expanduser().resolve()
        if args.archive_root
        else (state_dir / "archive" / "sessions")
    )
    lock_path = archive_root / args.agent_id / ".archive.lock"
    ensure_parent(lock_path)

    with lock_path.open("w") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as err:
            raise SystemExit("Archive job already running") from err
        result = run_archive(
            state_dir=state_dir,
            agent_id=args.agent_id,
            keep_count=args.keep_count,
            keep_days=args.keep_days,
            archive_root=archive_root,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

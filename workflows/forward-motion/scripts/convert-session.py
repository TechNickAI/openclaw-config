#!/usr/bin/env python3
"""Convert tgcli's gotd session format to a Telethon SQLite session.

tgcli stores its session in ~/.tgcli/session.json (Go gotd format).
Telethon needs a .session SQLite file. This script bridges them.

Usage:
    python3 convert-session.py [--output ~/.tgcli/telethon-session] [--force]
"""

import argparse
import base64
import json
import sqlite3
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

DC_ADDRESSES = {
    1: "149.154.175.53",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130",
}

DEFAULT_OUTPUT = "~/.tgcli/telethon-session"


def convert(
    tgcli_dir: str = "~/.tgcli",
    output: str = DEFAULT_OUTPUT,
    force: bool = False,
) -> Path:
    store = Path(tgcli_dir).expanduser()
    session_path = store / "session.json"

    if not session_path.exists():
        print(
            f"ERROR: {session_path} not found. Is tgcli authenticated?",
            file=sys.stderr,
        )
        sys.exit(1)

    sess = json.loads(session_path.read_text())
    data = sess.get("Data", {})
    dc_id = data.get("DC", 1)
    addr = data.get("Addr", "") or DC_ADDRESSES.get(dc_id, "")
    auth_key = base64.b64decode(data["AuthKey"])

    if len(auth_key) != 256:
        print(
            f"ERROR: AuthKey is {len(auth_key)} bytes, expected 256",
            file=sys.stderr,
        )
        sys.exit(1)

    if ":" in addr:
        host, port_s = addr.rsplit(":", 1)
        port = int(port_s)
    else:
        host = addr
        port = 443

    db_path = Path(f"{output}").expanduser().with_suffix(".session")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists() and not force:
        modified_at = datetime.fromtimestamp(db_path.stat().st_mtime, tz=UTC)
        if datetime.now(tz=UTC) - modified_at < timedelta(hours=24):
            print(
                f"Telethon session is fresh, skipping conversion: {db_path}",
            )
            return db_path
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute(
        """CREATE TABLE sessions (
        dc_id INTEGER PRIMARY KEY, server_address TEXT,
        port INTEGER, auth_key BLOB, takeout_id INTEGER
    )"""
    )
    c.execute(
        """CREATE TABLE entities (
        id INTEGER PRIMARY KEY, hash INTEGER NOT NULL,
        username TEXT, phone INTEGER, name TEXT, date INTEGER
    )"""
    )
    c.execute(
        """CREATE TABLE sent_files (
        md5_digest BLOB, file_size INTEGER, type INTEGER,
        id INTEGER, hash INTEGER,
        PRIMARY KEY (md5_digest, file_size, type)
    )"""
    )
    c.execute(
        """CREATE TABLE update_state (
        id INTEGER PRIMARY KEY, pts INTEGER, qts INTEGER,
        date INTEGER, seq INTEGER
    )"""
    )
    c.execute("CREATE TABLE version (version INTEGER PRIMARY KEY)")
    # Telethon SQLite schema version pinned to 7.
    c.execute("INSERT INTO version VALUES (7)")
    c.execute(
        "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
        (dc_id, host, port, auth_key, None),
    )
    conn.commit()
    conn.close()

    print(f"Created telethon session: {db_path}")
    print(f"  DC={dc_id} host={host} port={port} key={len(auth_key)}b")
    return db_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert tgcli session to Telethon",
    )
    parser.add_argument(
        "--tgcli-dir",
        default="~/.tgcli",
        help="tgcli store directory",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output path (without .session)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recreate the Telethon session even if existing one is less than 24h old",
    )
    args = parser.parse_args()
    convert(args.tgcli_dir, args.output, force=args.force)

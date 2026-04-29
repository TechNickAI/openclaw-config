---
name: tgcli-topics
version: 0.2.0
description:
  List, discover, and search Telegram forum topics using the Telegram Client API
  (MTProto) via Telethon. Use when you need to find topic IDs (thread IDs) for a
  Telegram chat, especially when the standard tgcli cannot list forum topics.
triggers:
  - telegram topics
  - forum topics
  - telegram threads
  - list topics
  - discover topics
  - find topic id
  - tgcli topics
metadata:
  openclaw:
    emoji: "🧵"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/tgcli-topics
    category: integrations
    requires:
      bins: [tgcli, python3]
---

# tgcli-topics

A specialized skill to discover and list Telegram forum topics. Standard `tgcli` is
great for flat-chat history, but it does not expose forum-topic listing. This skill
bridges the gap by converting the `tgcli` session to a Telethon session and querying the
MTProto Client API directly.

## Ready-to-run entrypoint

Use the wrapper below as the default command. It bootstraps a local Telethon virtualenv
in `~/.tgcli/venv`, installs `telethon` if needed, converts the `tgcli` session to a
Telethon `.session` file when missing or stale, and then runs topic discovery.

```bash
# List topics for all dialogs (Markdown format)
python3 scripts/tgcli-topics.py --all --markdown

# List topics for specific peers
python3 scripts/tgcli-topics.py --peers 123456789,987654321

# Output as JSON
python3 scripts/tgcli-topics.py --all --json
```

## Helper scripts

- `scripts/tgcli-topics.py` is the only entrypoint agents should need.
- `scripts/convert-session.py` remains available for forced/manual conversion.
- `scripts/discover-topics.py` remains available as the lower-level discovery helper.

## Notes

- First run may take a moment because the wrapper may create a venv and install
  `telethon`.
- Topic discovery paginates, so chats with more than 100 topics are handled correctly.
- `--include-flat` includes dialogs that do not have forum topics, which is useful for
  audits.
- For topic _message reads_ in bot DMs, use a Telethon client with
  `receive_updates=False`. In practice, isolating each bot DM in its own client pass
  avoids update-decoding issues while reading replies.

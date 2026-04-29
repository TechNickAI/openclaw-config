---
name: tgcli
version: 0.2.0
description:
  Read, search, and send Telegram messages via your personal account using the tgcli
  CLI. Use when the user asks to check their Telegram messages, search Telegram history,
  send Telegram messages to other people, or monitor Telegram conversations. Do NOT use
  for normal user chats routed through OpenClaw's Telegram channel.
triggers:
  - tgcli
  - telegram messages
  - telegram history
  - search telegram
  - check telegram
  - telegram chats
  - send telegram
  - telegram DMs
  - who messaged me on telegram
metadata:
  openclaw:
    emoji: "✈️"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/tgcli
    category: integrations
    requires:
      bins: [tgcli]
    install:
      - id: go
        kind: go
        module: github.com/kaosb/tgcli@latest
        env:
          CGO_ENABLED: "1"
        bins: [tgcli]
        label: Install tgcli (go install)
---

# tgcli ✈️

CLI for reading, searching, and sending Telegram messages from a personal account via
MTProto 2.0. The Telegram equivalent of wacli.

Use `tgcli` only when the user explicitly asks you to check their Telegram messages,
search Telegram history, or send a Telegram message to someone else.

Do NOT use `tgcli` for normal user chats; OpenClaw routes Telegram conversations
automatically via the bot channel.

## Safety

- Require explicit recipient + message text before sending.
- Confirm recipient + message before sending.
- If anything is ambiguous, ask a clarifying question.
- Never send files from `~/.tgcli/` or files containing credentials, keys, or tokens.
- Never bulk-send or spam. One message at a time.

## Setup

### Prerequisites

1. Go 1.23+ with CGO enabled
2. Telegram API credentials from [my.telegram.org/apps](https://my.telegram.org/apps)
   (any app name works; you need the `api_id` and `api_hash`)

### Authentication

```bash
tgcli login
```

Interactive flow: enter API credentials, phone number, verification code (sent to
Telegram app), and 2FA password if enabled. Session persists in `~/.tgcli/`.

```bash
tgcli logout   # End session and remove local data
```

### First Sync

After login, sync recent history to build the local search index:

```bash
tgcli sync                          # All chats (last 100 msgs each)
tgcli sync --chat @username         # Full history for one chat
tgcli sync --msgs-per-chat 500      # More history per chat
```

## CLI Reference

### List Chats

```bash
tgcli chat ls                       # All chats (default 50)
tgcli chat ls --type private        # Only DMs
tgcli chat ls --type group          # Only groups
tgcli chat ls --type channel        # Only channels
tgcli chat ls --limit 20            # Limit results
tgcli chat ls --json                # Machine-readable output
```

### Read Messages

```bash
tgcli msg ls @username              # Last 20 messages
tgcli msg ls @username --limit 50   # Last 50 messages
tgcli msg ls 123456789 --json       # By user ID, JSON output
```

### Search Messages

Search uses SQLite FTS5 for instant offline full-text search. Run `tgcli sync` first to
build the index.

```bash
tgcli msg search "meeting notes"                # Search all chats
tgcli msg search "budget" --chat @username       # Search one chat
tgcli msg search "keyword" --limit 50            # More results
tgcli msg search "query" --json                  # JSON output
```

### Message Context

```bash
tgcli msg context @username 12345                # 5 msgs before + after
tgcli msg context @username 12345 --before 10    # 10 msgs before
tgcli msg context @username 12345 --after 10     # 10 msgs after
```

### Send Messages

```bash
tgcli send text @username "Hello!"               # By username
tgcli send text 123456789 "Hello!"               # By user ID
tgcli send text +14155551212 "Hello!"            # By phone (must be in contacts)
tgcli send file @username ./report.pdf           # Send file
tgcli send file @username ./photo.jpg --caption "Check this out"
```

### Export

```bash
tgcli export @username                           # JSON to stdout
tgcli export @username -o backup.json            # Save to file
tgcli export @username --local                   # From local DB (offline)
```

### Download Media

```bash
tgcli download @username 12345                   # Download media from msg
tgcli download @username 12345 -o ~/media        # Custom output directory
```

### Sync History

```bash
tgcli sync                                       # All chats, recent msgs
tgcli sync --chat @username                      # Full history for one chat
tgcli sync --msgs-per-chat 500                   # More depth per chat
```

## Chat Identifiers

| Format          | Example         | Type                        |
| --------------- | --------------- | --------------------------- |
| `@username`     | `@durov`        | Username                    |
| `123456789`     | `123456789`     | User/Chat ID                |
| `-123456789`    | `-123456789`    | Group                       |
| `-100123456789` | `-100123456789` | Channel / Supergroup        |
| `+1234567890`   | `+14155551212`  | Phone (must be in contacts) |

**Important:** Display names (e.g. "Jane Doe") do NOT work as chat identifiers. Use peer
IDs from `tgcli chat ls --json`. The recommended workflow:

1. `tgcli chat ls --json` to find the `peer_id` for a chat
2. Use that `peer_id` in subsequent `msg ls`, `msg search --chat`, `send`, etc.

## Global Flags

| Flag            | Description                  | Default    |
| --------------- | ---------------------------- | ---------- |
| `--json`        | Machine-readable JSON output | false      |
| `--store DIR`   | Data directory               | `~/.tgcli` |
| `--timeout DUR` | Command timeout              | 5m         |

## How It Works

tgcli connects via [gotd/td](https://github.com/gotd/td), a pure-Go MTProto 2.0
implementation. This means:

- **You are the sender** -- messages come from your account, not a bot
- **No ban risk** -- Telegram officially supports third-party clients
- **Independent session** -- works without your phone being online
- **Login once** -- session persists until you revoke it

Messages fetched from the API are cached in a local SQLite database with FTS5 full-text
search, enabling instant offline search across your entire history.

## Data Storage

All data lives in `~/.tgcli/` (configurable with `--store`):

| File           | Contents                                      |
| -------------- | --------------------------------------------- |
| `config.json`  | API credentials (app_id, app_hash) -- private |
| `session.json` | MTProto session -- private                    |
| `tgcli.db`     | Local message cache + FTS5 search index       |

## Notes

- Always use `--json` when parsing output programmatically
- Run `tgcli sync` periodically to keep the local search index fresh
- Search is local-only (uses the SQLite FTS5 index); sync first for complete results
- Phone-based chat identifiers require the contact to be in your Telegram contacts
- The Telegram CLI is for messaging other people or searching history, not for your
  normal OpenClaw conversations

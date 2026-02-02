---
name: apple-mail
version: 0.1.0
description: Apple Mail.app integration for macOS. Read, search, send, reply, and manage emails via PyObjC ScriptingBridge.
triggers:
  - apple-mail
  - mail
  - email
  - inbox
metadata:
  openclaw:
    emoji: "📧"
    os: ["darwin"]
    requires:
      apps: ["Mail.app"]
---

# Apple Mail

Interact with Mail.app via PyObjC ScriptingBridge. Requires Mail.app to be running.

## Commands

| Command | Usage |
|---------|-------|
| **help** | `apple-mail help` |
| **accounts** | `apple-mail accounts` |
| **mailboxes** | `apple-mail mailboxes [account]` |
| **list** | `apple-mail list [mailbox] [--account X] [--limit N]` |
| **search** | `apple-mail search "query" [--limit N]` |
| **read** | `apple-mail read <id> [id...]` |
| **delete** | `apple-mail delete <id> [id...]` |
| **move** | `apple-mail move <mailbox> <id> [id...]` |
| **mark-read** | `apple-mail mark-read <id> [id...]` |
| **mark-unread** | `apple-mail mark-unread <id> [id...]` |
| **refresh** | `apple-mail refresh [account]` |
| **send** | `apple-mail send --to X --subject Y --body Z [--from account]` |
| **reply** | `apple-mail reply <id> --body "text" [--all]` |

## Output Format

List/search returns: `ID | ReadStatus | Date | Sender | Subject`
- `●` = unread, blank = read

## Mailbox Names

For Gmail accounts, use standard mailbox names:
- `INBOX` — Primary inbox
- `[Gmail]/Sent Mail` — Sent emails
- `[Gmail]/Trash` — Trash
- `[Gmail]/Spam` — Spam
- Custom labels work without prefix

For local mailboxes ("On My Mac"):
- `Agent-Archived` — Searchable history
- `Agent-Deleted` — 30-day quarantine
- `Agent-Reviewed` — Processed but kept
- `Agent-Starred` — Needs attention
- `Agent-Unsubscribe` — Unsubscribe candidates

## Examples

```bash
# List recent inbox messages
apple-mail list INBOX --limit 20

# Search for emails from a sender
apple-mail search "from:github.com" --limit 10

# Read a specific email
apple-mail read 12345

# Move to archive
apple-mail move Agent-Archived 12345 12346 12347

# Mark as read
apple-mail mark-read 12345

# Send an email
apple-mail send --to "friend@example.com" --subject "Hello" --body "How are you?"

# Reply to a message
apple-mail reply 12345 --body "Thanks for the update!"
```

## Errors

| Error | Cause |
|-------|-------|
| `Mail.app is not running` | Open Mail.app before running |
| `Account not found` | Invalid account name — check `accounts` |
| `Mailbox not found` | Invalid mailbox — check `mailboxes` |
| `Message not found` | Invalid/deleted ID — get fresh from `list` |

## Notes

- Message IDs are Mail.app internal IDs; get fresh ones from list/search
- Confirm recipient before sending
- Move command works with both Gmail IMAP and local mailboxes

# Task Management System

## Overview

Track ALL requests in `memory/tasks.md` using GitHub-style checkboxes. No dropped balls.

## The File: `memory/tasks.md`

```markdown
## Active
- [ ] **[whatsapp]** Research restaurant recommendations 🟡
- [ ] 🔄 **[slack]** Build API integration

## Blocked
- [ ] 💤 **[whatsapp]** Send flowers — blocked on: date confirmation (check back: 2026-01-30)

## Completed Today
- [x] **[imessage]** Reply to Anna about dinner ✅

## Archive
### 2026-01-29
- [x] **[whatsapp]** Set up cron job ✅
```

## Markers

| Marker | Meaning |
|--------|---------|
| `- [ ]` | Pending |
| `- [x]` | Completed |
| 🔴 | Urgent priority |
| 🟡 | High priority |
| ⚪ | Normal (default, can omit) |
| 🔄 | In progress (I'm working on it) |
| 💤 | Blocked (waiting on something) |
| ⏳ | Scheduled/waiting for time |
| ✅ | Done marker (for archive clarity) |

## When to Add a Task

1. **Anything >30 seconds** — If it takes real work, track it
2. **Multi-step processes** — Might get interrupted
3. **Blocked on input** — Need info from user or external source
4. **Explicit request** — "Remember to...", "TODO:", "Follow up on..."
5. **Sub-agent spawned** — Track what it's doing

## When NOT to Add

- Quick answers (<30s)
- Simple lookups
- Conversational replies

## Lifecycle

```
Add to Active → Work on it (🔄) → Complete (move to Completed Today)
      ↓
  Blocked? → Move to Blocked with reason + check-back date
      ↓
  Unblocked → Move back to Active → Complete
```

## Heartbeat Checks

Every heartbeat, scan `memory/tasks.md`:
1. Any 💤 blocked tasks past check-back date? → Re-attempt or ping user
2. Any 🔄 in-progress with no sub-agent running? → Resume or note interruption
3. Any stale items in Active? → Either work on them or ask for clarification

## Archiving

- **End of day:** Move "Completed Today" to "Archive" under date header
- **Weekly:** Move tasks older than 7 days to `memory/tasks-archive.md`
- **Keep archive searchable** — It's memory of what we've done together

## Channel Tags

Always tag the source channel:
- `**[whatsapp]**`
- `**[slack]**`
- `**[imessage]**`
- `**[discord]**`
- `**[voice]**` (for voice commands)
- `**[webchat]**`

This helps track where to send updates.

## Examples

**Quick task:**
```markdown
- [ ] **[whatsapp]** Look up best tacos in Austin 🟡
```

**Blocked task:**
```markdown
- [ ] 💤 **[slack]** Schedule team dinner — blocked on: venue preferences (check back: 2026-01-30)
```

**In-progress with sub-agent:**
```markdown
- [ ] 🔄 **[whatsapp]** Research hotels — subagent:abc123 running
```

**Completed:**
```markdown
- [x] **[whatsapp]** Set up search plugin ✅
```

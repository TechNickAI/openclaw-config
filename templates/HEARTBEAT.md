# HEARTBEAT.md

## Task Check (Priority 1)
- Read `memory/tasks.md`
- Any 💤 blocked tasks past `checkBackAt`? → Re-attempt or ping {{USER_NAME}}
- Any 🔄 in-progress tasks with stale/dead sub-agents? → Clean up or retry
- Any `pending` tasks sitting >2h? → Start or ask for clarification

## Periodic Checks (Rotate, 1-2 per heartbeat)
- [ ] Urgent emails (check if >4h since last check)
- [ ] Calendar next 24h (check if >8h since last check)

## Rules
- Late night (23:00-08:00): task checks only, skip periodic unless urgent
- If all clear: HEARTBEAT_OK
- If action needed: handle it, don't just report

---

## Customization

Edit this file to add your own periodic checks:

```markdown
## Custom Checks
- [ ] Check [service] for [thing]
- [ ] Review [folder] for [condition]
```

Keep this file small to minimize token usage on every heartbeat.

**Placeholder Reference:**
- `{{USER_NAME}}` — The human's name

# HEARTBEAT.md

## Periodic Checks (Rotate, 1-2 per heartbeat)

- [ ] Urgent emails (check if >4h since last check)
- [ ] Calendar next 24h (check if >8h since last check)

## Daily Checks

- [ ] Config updates: check if openclaw-config has updates, apply them if available

## Rules

- Late night (23:00-08:00): skip periodic unless urgent
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

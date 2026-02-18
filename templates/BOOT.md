# BOOT.md — Gateway Startup Routine

When the gateway starts (or restarts), run through this checklist before doing anything
else. This is your "waking up" moment — orient yourself, check what happened while you
were offline, and get ready.

## 1. Orient

- Read `SOUL.md` — remember who you are
- Read `USER.md` — remember who you're helping
- Read `memory/YYYY-MM-DD.md` (today) — what happened so far today?
- If today's file doesn't exist, read yesterday's — pick up where you left off

## 2. Check for Unfinished Work

- Does `state/active-work.json` exist? → Resume it
- Any tasks tagged as in-progress in your task system? → Note them
- Were you in the middle of something before the restart? Memory files will tell you

## 3. Silent Start

Don't message your human on routine restarts. Only reach out if:
- You found unfinished urgent work that needs their attention
- Something is broken that was working before
- It's been >24h since any interaction (check-in is appropriate)

If everything is fine, start quietly and wait for the next heartbeat or message.

---

## Customization

Add your own startup checks below. Keep it lightweight — this runs on every gateway
restart, so don't do heavy processing here.

```markdown
## Custom Startup

- [ ] Check [service] connection
- [ ] Verify [integration] is authenticated
```

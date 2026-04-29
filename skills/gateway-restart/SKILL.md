---
name: gateway-restart
version: 0.2.0
description:
  Graceful gateway restart — waits for active queries and cron jobs to complete
triggers:
  - gateway restart
  - restart gateway
  - graceful restart
metadata:
  openclaw:
    emoji: "🔄"
    homepage: https://github.com/TechNickAI/openclaw-config/tree/main/skills/gateway-restart
    category: operations
    requires:
      bins: [openclaw]
---

# Gateway Restart Skill 🔄

Gracefully restarts the OpenClaw gateway by waiting for active queries and cron jobs to
complete before restarting. Prevents mid-conversation interruptions.

**Users say things like:**

- "Restart the gateway gracefully"
- "Is the gateway busy right now?"
- "Restart the gateway on the remote machine"

---

## Commands

- `gateway-restart restart` — Wait for active work to finish, then restart
- `gateway-restart status` — Check if anything is actively running (no restart)
- `gateway-restart restart --force` — Skip waiting, restart immediately
- `gateway-restart restart --timeout 300` — Custom wait timeout in seconds
  (default: 300)
- `gateway-restart restart --remote <host>` — Restart a remote fleet machine via SSH

## Detection Strategy

1. **Session age check** — Query `openclaw gateway call status --json` for sessions
   updated in the last 60 seconds
2. **Log confirmation** — If sessions look active, parse today's gateway log for
   unmatched `inbound web message` without a subsequent `auto-reply sent`
3. **Cron job check** — Query `openclaw cron list --json` for currently-running jobs

## Setup

No setup required. Uses `openclaw` CLI commands available on any OpenClaw installation.

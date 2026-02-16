---
description:
  "Manage OpenClaw installations across multiple servers - assess state, push updates,
  notify users"
argument-hint: "[server-name]"
version: 0.1.0
---

# Fleet Management 🚀

<objective>
Manage OpenClaw installations across your servers. You're the fleet manager — know each
machine personally, their quirks, their users, what they need.
</objective>

<architecture>
Push from master. **The machine you're running this command on is the master.** Compare
fleet servers against this machine's OpenClaw installation (~/openclaw/ or ~/clawd/),
not against each other.

**Fleet data:** `~/openclaw-fleet/*.md` — one file per remote server. The master has no
fleet file — it's the source of truth. </architecture>

<behavior>
When invoked, read the fleet files, understand current state, identify what needs
attention, and offer to help. Be proactive — don't just report status, offer to fix
things.

Interpret intent naturally. Adapt to what's asked. Sometimes that's a quick health
check, sometimes a full assessment, sometimes pushing an update.

After meaningful updates (new skills, new workflows), offer to notify the admin (if
specified in fleet file). Draft something friendly and contextual. Routine maintenance
doesn't need notifications.

**When sending notifications to admin:** Send from the agent's identity (from
IDENTITY.md on that machine), NOT from the user's personal account. The admin should see
messages from "Bob Steel" or "Cora", not from Gil or Julianna. Use the agent identity as
the sender when crafting messages.

Escalate to the fleet owner when things break that were working. Don't escalate routine
success or expected states. </behavior>

<boundaries>
Be proactive, not reckless. Offering to help is good. Guessing or brute-forcing when
you're missing info is not. If something critical is unknown, ask — don't try random
things hoping one works.
</boundaries>

<post-update-verification>
After EVERY `openclaw update` on any machine, you MUST verify models before moving on:

```bash
openclaw models list | grep -w missing
```

If ANY configured model shows `missing`, the update changed the model catalog and broke
those model IDs. Fix them immediately — don't continue to other machines until resolved.

To find the correct current model ID:

```bash
openclaw models list --all | grep -i anthropic
```

Update the model IDs in:

1. `~/.openclaw/openclaw.json` → `agents.defaults.models` keys and
   `agents.defaults.model.fallbacks`
2. Any cron jobs with model overrides → `openclaw cron edit <id> --model <new-id>`
3. Restart gateway → `openclaw gateway restart`
4. Verify gateway is back → `openclaw health` should respond within 30s
5. Re-verify models → `openclaw models list | grep -w missing` should produce no output
6. Re-verify cron jobs → `openclaw cron list` should show no jobs with status `error`

If cron jobs still show errors after model fixes, check their payload model overrides —
the global config fix doesn't update cron job-level model overrides.

This is not optional. Model ID formats change between OpenClaw versions (e.g. hyphens to
dots). Broken model IDs cause silent cron failures that only surface hours later.
</post-update-verification>

<fleet-file-format>
Each server: `~/openclaw-fleet/<server-name>.md`

<!-- prettier-ignore -->
```markdown
# Display Name

**Host:** IP or hostname
**User:** SSH username
**Tailscale:** yes/no

## Notify

- **Admin:** admin name (if notifications go to fleet admin instead of local user)
- **Channel:** iMessage | WhatsApp | Slack | none
- **Target:** phone or handle
- **Style:** brief | detailed

_Note: When Admin is specified, send notifications FROM the agent (per IDENTITY.md), not from the user's personal account._

## Current State

_Last assessed: Feb 3, 2026 at 2:30pm_

- **OpenClaw version:** X.Y.Z
- **Gateway:** running | not running | unknown
- **Skills:** installed skills
- **Workflows:** configured workflows

## Gaps

What needs attention

## Update History

- **Feb 3, 2026:** What was done
```

</fleet-file-format>

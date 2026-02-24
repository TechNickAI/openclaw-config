# Notification Routing — Definitive Process

OpenClaw fleet notifications use a **two-lane model**: admin lane for system health,
user lane for cron outputs. Never mix them.

## Lane 1: Admin (System Health → Nick)

**What:** Health check results, cron job failures, infrastructure issues, gateway
problems, model errors, anything BROKEN.

**Recipient:** Nick (fleet admin) — Telegram `469214633`

**Mechanism:** `~/.openclaw/health-check-admin` file on each machine.

**Standard format (exactly 2 lines):**

```
Nick
openclaw message send --channel telegram --target "469214633" --message "{MESSAGE}"
```

**Jobs that use this lane:**

- Health Check cron (reads health-check-admin, sends via the command in line 2)
- Fleet management operations (reads fleet file Admin section)

**Rules:**

- Health check cron jobs MUST have `delivery.mode: "none"` — the agent handles its own
  notifications via health-check-admin. Using announce/deliver modes causes duplicate or
  broken delivery.
- Never hardcode Nick's contact in cron job prompts on fleet machines. Always reference
  the health-check-admin file so the target can be updated in one place.
- Admin notifications include the hostname and agent identity (from IDENTITY.md).

## Lane 2: User (Cron Outputs → Host Person)

**What:** EOD briefings, email alerts, stock alerts, WhatsApp reviews, morning previews,
commitment extracts — anything produced FOR the user.

**Recipient:** The person hosting the instance.

**Mechanism:** Two options (use whichever fits the job):

1. **Delivery config** — set `delivery.mode: "announce"` with `delivery.channel` and
   `delivery.to` pointing to the user's Telegram ID. OpenClaw auto-delivers the output.
2. **In-prompt messaging** — the cron prompt explicitly tells the agent to use the
   message tool to send to the user's channel/ID. Use when you need conditional
   notifications (e.g., "only notify if there are follow-ups").

**User Telegram IDs:**

| Machine             | User         | Telegram ID | Bot                |
| ------------------- | ------------ | ----------- | ------------------ |
| Master              | Nick         | 469214633   | Cora's bot         |
| Gil's Mac Mini      | Gil Penchina | 6234387199  | @Gils_bob_bot      |
| Thomas's Mac Mini   | Thomas Owen  | 8546096241  | @thomas_roxy_bot   |
| Ali's Mac Mini      | Ali Katz     | 1168760671  | ShantiMa's bot     |
| Julianna's Mac Mini | Julianna     | TBD         | @Juliannas_Ace_bot |

**Rules:**

- User-facing jobs target the HOST user, not the fleet admin.
- On the master (Nick's machine), admin and user are the same person — no conflict.
- On fleet machines, cron prompts that mention "Nick" or hardcode `469214633` for
  user-facing output are WRONG unless the job is system health.

## Job Classification Guide

| Classification | Description                                                           | Lane    | delivery.mode                                       |
| -------------- | --------------------------------------------------------------------- | ------- | --------------------------------------------------- |
| **System**     | Health checks, update checks, infrastructure monitoring               | Admin   | `none` (agent self-notifies via health-check-admin) |
| **User**       | Briefings, reviews, alerts, stewards that produce output for the user | User    | `announce` or `none` with in-prompt messaging       |
| **Internal**   | Librarian, memory org, knowledge extraction — no notification needed  | Neither | `none`                                              |

## Setting Up a New Fleet Machine

1. **Create health-check-admin** (admin lane):

   ```
   Nick
   openclaw message send --channel telegram --target "469214633" --message "{MESSAGE}"
   ```

2. **Find the user's Telegram ID**:

   ```python
   # On the machine, use its bot token to query:
   # GET https://api.telegram.org/bot<TOKEN>/getChat?chat_id=<ID>
   # Check the bot's allowFrom list in openclaw.json for candidate IDs
   ```

3. **Configure user-facing cron jobs** with the user's Telegram ID in delivery config or
   prompt text.

4. **Update the fleet file** (`~/openclaw-fleet/<machine>.md`) with both Admin and User
   Notify sections.

## Vestigial Delivery Configs

Some cron jobs have `delivery.mode: "none"` but still have `channel` and `to` fields
populated (e.g., `{"mode": "none", "channel": "whatsapp", "to": "+19253537603"}`). The
extra fields are ignored when mode is `none`. They're harmless but misleading — clean
them up when you touch the job.

## Troubleshooting

**"cron announce delivery failed"**: The `delivery.mode: announce` is trying to send via
a channel that can't reach the target. Common causes:

- Target hasn't /started the bot (Telegram bots require the user to initiate)
- Wrong chat ID
- Channel not configured on that machine's gateway

**Health check not notifying admin**: Check `~/.openclaw/health-check-admin` has exactly
2 lines and the command format is correct. Test by running the command manually with a
test message.

**Notifications going to wrong person**: Check the fleet file's Notify section — if
admin and user IDs are swapped, fix health-check-admin (admin lane) and cron delivery
configs (user lane) independently.

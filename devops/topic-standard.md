# Topic Standard — Telegram Forum Routing

Every OpenClaw instance that uses Telegram forums (group with topics enabled) follows
this standard for organizing bot output.

## Required Topics (every instance)

| Name              | Purpose                                                                                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **🏠 Home**       | Direct conversation with the bot. Personal messages, interactive sessions, anything conversational. The "default room."                                   |
| **📋 Automation** | Default destination for all scheduled job output. Briefings, steward alerts, recurring reports. If a job doesn't have a more specific home, it goes here. |
| **⚙️ System**     | Infrastructure health, update notifications, fleet announcements. Should be quiet 95%+ of the time. Only system-level operational messages.               |

**Naming rule:** Include a leading emoji in topic names (e.g. "🏠 Home"). Telegram
renders the leading emoji as the topic icon in the sidebar. This is the simplest way to
get a recognizable icon without querying Telegram's custom emoji sticker IDs. The emoji
will appear both in the icon bubble and the name text, which is fine.

## Optional Topics (per-instance, based on volume)

Instances with high job counts may add purpose-specific topics to reduce noise in
Automation. Examples:

| Name              | When to add                      | Example jobs                                  |
| ----------------- | -------------------------------- | --------------------------------------------- |
| **📬 Inboxes**    | 3+ inbox stewards running        | Email, Telegram, WhatsApp, Instagram stewards |
| **💤 Sleep**      | Sleep/lighting automation active | Sleep Brain, Wind-Down, Melatonin             |
| **💼 Job Search** | Active job search pipeline       | Job Search Guru, recruiter alerts             |
| **🎲 Fun**        | Multiple fun/lifestyle jobs      | Powerball, birthday alerts                    |

**Rule of thumb:** Don't create a topic for fewer than 2 jobs. Automation handles
everything until volume justifies splitting.

## Routing Rules

### For each cron job, determine its destination:

1. **Does this job produce user-visible output?**
   - No → `delivery: none`, no topic. (Internal jobs: cortex, reflection, sentinels with
     no findings, etc.)
   - Yes → continue.

2. **Is it conversational / personal?**
   - Yes → 🏠 Home. (Daily check-in, interactive sessions.)

3. **Is it a system/infrastructure message?**
   - Yes → ⚙️ System. (Health failures, update alerts, auth failures, fleet
     announcements.)

4. **Does an optional topic exist that's a better fit?**
   - Yes → Route there. (Inbox steward → 📬 Inboxes, if that topic exists.)

5. **Default → 📋 Automation.**

### Delivery mechanism

Jobs should use ONE delivery method, not both:

- **`delivery.mode: "announce"`** with `channel`, `to`, and topic thread ID — for jobs
  that always produce output (briefings, reports).
- **In-prompt `message` tool** with explicit channel/target/threadId — for jobs that
  conditionally notify (stewards that only alert when something needs attention).
- **Never both.** Double delivery = duplicate messages.

When using in-prompt messaging, the job prompt must include the thread ID for the
correct topic. Template:

```
When you need to notify, use the message tool:
- action: send
- channel: telegram
- target: <USER_TELEGRAM_ID>
- threadId: <TOPIC_THREAD_ID>
```

### Silent jobs

Jobs that do internal work (knowledge extraction, memory maintenance, task management)
use `delivery: { mode: "none" }` and do NOT post to any topic unless they discover
something that needs human attention — in which case they post to the appropriate topic
via in-prompt messaging.

## Fleet Setup Procedure

### Creating topics for a new instance

1. Ensure the Telegram group has forum/topics enabled.
2. Create the three required topics using the message tool:
   ```
   action: topic-create
   channel: telegram
   target: <GROUP_CHAT_ID>
   name: "🏠 Home"
   ```
3. Record the returned topic thread IDs in the fleet file
   (`~/openclaw-fleet/<machine>.md`) under a `## Topics` section.
4. Update all cron jobs to reference the correct thread IDs.

### Fleet file topic section format

```markdown
## Topics

| Topic         | Thread ID | Purpose                         |
| ------------- | --------- | ------------------------------- |
| 🏠 Home       | <id>      | Conversation                    |
| 📋 Automation | <id>      | Scheduled job output            |
| ⚙️ System     | <id>      | Health, updates, fleet          |
| 📬 Inboxes    | <id>      | Inbox steward alerts (optional) |
```

## Cross-Channel Jobs

Some jobs deliver to non-Telegram channels. These are exceptions to the topic routing
and should be documented in the cron manifest:

- Slack channel posts → use `channel: slack` with target channel ID
- WhatsApp messages → use `channel: whatsapp` with target number

These jobs do not use Telegram topics at all.

## Vestigial Config Cleanup

When updating jobs to this standard, clean up:

- Remove `delivery.channel` and `delivery.to` when `delivery.mode` is `"none"`
- Remove `sessionKey` references to old thread IDs that no longer apply
- Standardize: if a job uses in-prompt messaging, set `delivery: { mode: "none" }`
- Standardize: if a job uses announce delivery, remove in-prompt message instructions

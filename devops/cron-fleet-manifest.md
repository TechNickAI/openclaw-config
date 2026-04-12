# Cron Fleet Manifest

Single source of truth for every scheduled job: what it does, where it runs, where its
output goes.

See `topic-standard.md` for the routing rules and topic definitions.

---

## Cora (Nick's Mac Studio) — Master Instance

### Topic Map

| Topic         | Thread ID | Purpose                                   |
| ------------- | --------- | ----------------------------------------- |
| 🏠 Home       | 70101     | Direct conversation, personal messages    |
| 📋 Automation | 70103     | Default for all scheduled job output      |
| ⚙️ System     | 70104     | Health, updates, fleet announcements      |
| 📬 Inboxes    | 67809     | Inbox steward alerts (pre-existing topic) |

### Job Registry

| Job                             | Schedule           | Model          | Topic         | Delivery Method | Notes                         |
| ------------------------------- | ------------------ | -------------- | ------------- | --------------- | ----------------------------- |
| **DCOS Morning Standup**        | 8am daily          | haiku          | 📋 Automation | announce        |                               |
| **Daily Intelligence Briefing** | 7am daily          | sonnet         | 📋 Automation | announce        |                               |
| **Daily EOD Briefing**          | 7pm daily          | verify         | 📋 Automation | announce        |                               |
| **DCOS Weekly Review**          | Sun 6pm            | sonnet         | 📋 Automation | announce        |                               |
| **Cora's Daily Check-In**       | 10am weekdays      | sonnet         | 🏠 Home       | in-prompt       | Personal, not operational     |
| **Birthday Check**              | 8am daily          | default        | 📋 Automation | announce        |                               |
| **Powerball Jackpot Alert**     | 10am Tue/Thu/Sun   | default        | 📋 Automation | announce        |                               |
| **🧠 Sleep Brain**              | 7am daily          | llama-maverick | 📋 Automation | announce        |                               |
| **🌙 Evening Wind-Down**        | 8pm daily          | llama-maverick | 📋 Automation | announce        |                               |
| **💤 Melatonin Protection**     | 9:30pm daily       | llama-maverick | 📋 Automation | announce        |                               |
| **Job Search Guru**             | 9am/1pm/5pm        | haiku          | 📋 Automation | in-prompt       | Only notifies when findings   |
| **WhatsApp Group Reviewer**     | 10am daily         | sonnet         | 📋 Automation | in-prompt       | Only notifies with summary    |
| **DCOS Inbox Sentinel**         | hourly 8am-10pm    | haiku          | 📬 Inboxes    | in-prompt       | Only notifies unreplied items |
| **Telegram Steward**            | every 30m 8am-10pm | haiku          | 📬 Inboxes    | in-prompt       | Only notifies flagged DMs     |
| **WhatsApp DM Steward**         | :15/:45 8am-10pm   | haiku          | 📬 Inboxes    | in-prompt       | Only notifies flagged DMs     |
| **Instagram Steward**           | 9am/1pm/6pm        | sonnet         | 📬 Inboxes    | in-prompt       | Only notifies flagged DMs     |
| **Email Steward**               | every 30m 7am-10pm | haiku          | 📬 Inboxes    | in-prompt       | Only notifies starred emails  |
| **OpenClaw Health Check**       | every 30m          | haiku          | ⚙️ System     | in-prompt       | Only on failure               |
| **cron-healthcheck**            | :05 past hour      | haiku          | ⚙️ System     | in-prompt       | Only on failure               |
| **OpenClaw Update Check**       | 9am daily          | sonnet         | ⚙️ System     | in-prompt       | Only when update available    |
| **DCOS Limitless Sentinel**     | every 15m 7am-11pm | haiku          | (silent)      | none            | Internal processing           |
| **DCOS Fireflies Sentinel**     | every 2h 8am-6pm   | haiku          | (silent)      | none            | Internal processing           |
| **Nightly Reflection**          | 11pm daily         | opus           | (silent)      | none            | Internal self-improvement     |
| **Nightly Librarian**           | 3am daily          | sonnet         | (silent)      | none            | Internal memory maintenance   |
| **Task Steward**                | hourly 8am-10pm    | haiku          | (silent)      | none            | Internal task management      |
| **Contact Steward — iMessage**  | 7am daily          | haiku          | (silent)      | none            | Internal contact processing   |
| **Contact Steward — WhatsApp**  | 7:05am daily       | haiku          | (silent)      | none            | Internal contact processing   |
| **Calendar Steward**            | 8am daily          | haiku          | (silent)      | none            | Internal calendar prep        |
| **Security Sentinel**           | Mon 4am            | opus           | (silent)      | none            | Internal research             |
| **Slack AI Intel**              | 8:30am daily       | sonnet         | Slack         | in-prompt       | Cross-channel (C09DP7FEZDK)   |

### Disabled Jobs

| Job                         | Reason              |
| --------------------------- | ------------------- |
| Trademark Scam Monitor      | Inactive operation  |
| Julianna Photos iCloud Sync | One-shot, completed |

---

## Fleet Template

For other instances (Gil, Julianna, Thomas, Ali, Hex, Shelly), the minimum topic set is:

| Topic         | Purpose          |
| ------------- | ---------------- |
| 🏠 Home       | Conversation     |
| 📋 Automation | Scheduled output |
| ⚙️ System     | Health + updates |

Create additional topics only when job volume in a category exceeds 2+ jobs.

Record topic thread IDs in the fleet file under `## Topics`.

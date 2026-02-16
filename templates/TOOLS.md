# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's
unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills
without losing your notes, and share skills without leaking your infrastructure.

---

## Your Local Notes

<!-- Add your environment-specific notes below -->

### Contacts

<!-- Key contacts with their details -->
<!-- Example: -->
<!--
### Partner
- Phone: +1 xxx-xxx-xxxx
- iMessage: Yes
- WhatsApp: Yes
-->

### Calendar

<!-- Calendar configuration -->
<!-- Example: -->
<!--
- Primary: personal@email.com
- Work: work@company.com
-->

### Task Management

<!-- How tasks are created and tracked. AGENTS.md references this for the Q&A vs Task flow. -->
<!-- Example (Asana): -->
<!--
- Platform: Asana
- Workspace ID: 1234567890
- Project ID: 1234567890
- Assignee ID: 1234567890 (your assistant user)
- Tags: Status: Not Started (ID), working (ID)
- API: `curl -X POST 'https://app.asana.com/api/1.0/tasks' -H "Authorization: Bearer $ASANA_ACCESS_TOKEN" ...`
-->
<!-- Example (File-based): -->
<!--
- Platform: File-based
- Task file: ~/tasks.md
- Format: Markdown checklist
-->

### Integrations

<!-- API keys, services, accounts -->
<!-- Document what's configured, not the secrets themselves -->

---

Add whatever helps you do your job. This is your cheat sheet.

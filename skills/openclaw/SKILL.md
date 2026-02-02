---
name: openclaw
version: 0.2.0
description: Install, configure, and update openclaw-config
triggers:
  - openclaw
  - openclaw-config
  - set up openclaw
  - update openclaw
metadata:
  openclaw:
    emoji: "🐾"
---

# OpenClaw Config Skill 🐾

Manages your openclaw-config installation.

**Users say things like:**
- "Set up openclaw-config"
- "Update my openclaw config"
- "Force update openclaw" (overwrites their changes)
- "Check if openclaw has updates"

---

# Setup

Clone `https://github.com/TechNickAI/openclaw-config` to `~/.openclaw-config`.

Copy templates to workspace root (don't overwrite existing): AGENTS.md, SOUL.md, USER.md, TOOLS.md, HEARTBEAT.md, IDENTITY.md

Create memory folder structure and copy all skills.

## Memory Search

Needs embeddings for semantic search.

**Ask:** LM Studio (local, free, recommended) or OpenAI?

**LM Studio:** Server on port 1234, model `lmstudio-community/embedding-gemma-300m-qat`, configure gateway baseUrl to `http://127.0.0.1:1234/v1`

**OpenAI:** Get their API key, configure gateway baseUrl to `https://api.openai.com/v1`, model `text-embedding-3-small`

**Verify:** Create test file in memory/, index, search semantically, confirm it finds it, clean up.

## Personalization

Ask and replace in templates: `{{USER_NAME}}`, `{{ASSISTANT_NAME}}`, `{{TIMEZONE}}`, `{{PRIORITY_1}}`, `{{PRIORITY_2}}`

## Optional Skills

Ask if they use each, get API key if yes:
- **Limitless** — app.limitless.ai → Settings → Developer
- **Fireflies** — app.fireflies.ai → Integrations → Fireflies API
- **Quo** — my.quo.com → Settings → API

## Finish

Track version in `.openclaw/installed-version`. Tell them what's configured.

---

# Update

Compare `.openclaw/installed-version` with `~/.openclaw-config/VERSION`.

If newer: pull, update skills (safe to overwrite), update templates only if user hasn't modified them, update version file, report changes.

If user wants to force/overwrite: backup to `.openclaw/backup/` first.

---

# Status

Show installed version and skill versions. Fetch remote VERSION, report if updates available.

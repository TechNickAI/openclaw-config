---
name: openclaw
version: 0.2.1
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

Do these steps in order:

1. **Clone repo** to `~/.openclaw-config`

2. **Copy templates** to workspace root (don't overwrite existing): AGENTS.md, SOUL.md, USER.md, TOOLS.md, HEARTBEAT.md, IDENTITY.md

3. **Create memory folders:** `memory/people`, `memory/projects`, `memory/topics`, `memory/decisions`

4. **Copy skills** to `skills/`

5. **Configure memory search** — Required for semantic search to work. Ask: LM Studio (local, free, recommended) or OpenAI?
   - **LM Studio:** Server on port 1234, model `lmstudio-community/embedding-gemma-300m-qat`, configure gateway memorySearch.remote.baseUrl to `http://127.0.0.1:1234/v1`
   - **OpenAI:** Get their API key, configure gateway memorySearch.remote.baseUrl to `https://api.openai.com/v1`, model `text-embedding-3-small`
   - **Verify it works:** Create test file in memory/, index it, search for it, confirm it returns results, clean up

6. **Personalization** — Ask and replace in templates: `{{USER_NAME}}`, `{{ASSISTANT_NAME}}`, `{{TIMEZONE}}`, `{{PRIORITY_1}}`, `{{PRIORITY_2}}`

7. **Optional skills** — These are optional. Ask about each one individually, only configure if they say yes:
   - "Do you have a Limitless Pendant?" → If yes, get API key from app.limitless.ai → Settings → Developer
   - "Do you use Fireflies.ai for meeting transcripts?" → If yes, get API key from app.fireflies.ai → Integrations → Fireflies API
   - "Do you use Quo for business phone?" → If yes, get API key from my.quo.com → Settings → API

   Skip any they don't use. Don't assume they want all of them.

8. **Track version** in `.openclaw/installed-version`

9. **Summary** — Tell them what's configured

---

# Update

Compare `.openclaw/installed-version` with `~/.openclaw-config/VERSION`.

If newer: pull, update skills (safe to overwrite), update templates only if user hasn't modified them, update version file, report changes.

If user wants to force/overwrite: backup to `.openclaw/backup/` first.

---

# Status

Show installed version and skill versions. Fetch remote VERSION, report if updates available.

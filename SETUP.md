# Setup Instructions

**For Clawdbot to follow when user asks to set up openclaw-config.**

## Steps

### 1. Clone the repo

```bash
git clone https://github.com/TechNickAI/openclaw-config.git ~/.openclaw-config
```

If already exists, pull latest:
```bash
cd ~/.openclaw-config && git pull
```

### 2. Copy templates to workspace root

Copy these files from `~/.openclaw-config/templates/` to the workspace root:
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `TOOLS.md`
- `HEARTBEAT.md`
- `IDENTITY.md`

**Do NOT overwrite** if the file already exists.

### 3. Create memory folder structure

```bash
mkdir -p memory/people memory/projects memory/topics memory/decisions
```

### 4. Copy skills to workspace/skills/

```bash
mkdir -p skills
cp -r ~/.openclaw-config/skills/* skills/
```

### 5. Create MEMORY.md if it doesn't exist

Create an empty MEMORY.md template for the user to fill in.

### 6. Track installation

```bash
mkdir -p .openclaw
cat ~/.openclaw-config/VERSION > .openclaw/installed-version
```

### 7. Interactive personalization

**Ask the user these questions and update files with their answers:**

1. "What's your name?" → Replace `{{USER_NAME}}` in all files
2. "What would you like to call your AI assistant?" → Replace `{{ASSISTANT_NAME}}`
3. "What's your timezone?" (default: their system timezone) → Replace `{{TIMEZONE}}`
4. "What's your top priority? (e.g., Work, Family, Health)" → Replace `{{PRIORITY_1}}`
5. "What's your second priority?" → Replace `{{PRIORITY_2}}`

Use `sed` or edit the files directly to replace placeholders.

### 8. Skill setup (interactive)

For each skill, ask if they want to set it up:

---

#### Limitless Pendant

**Ask:** "Do you have a Limitless Pendant and want to set up the integration?"

If yes:
1. Tell them: "Get your API key from https://app.limitless.ai → Settings → Developer"
2. Ask: "Paste your Limitless API key:"
3. Configure it using gateway config.patch:

```json
{
  "env": {
    "LIMITLESS_API_KEY": "<their-key>"
  }
}
```

---

#### Fireflies.ai

**Ask:** "Do you use Fireflies.ai for meeting transcripts?"

If yes:
1. Tell them: "Get your API key from https://app.fireflies.ai → Integrations → Fireflies API"
2. Ask: "Paste your Fireflies API key:"
3. Configure it:

```json
{
  "env": {
    "FIREFLIES_API_KEY": "<their-key>"
  }
}
```

---

#### Quo (Business Phone)

**Ask:** "Do you use Quo (formerly OpenPhone) for business calls?"

If yes:
1. Tell them: "Get your API key from https://my.quo.com → Settings → API"
2. Ask: "Paste your Quo API key:"
3. Configure it:

```json
{
  "env": {
    "QUO_API_KEY": "<their-key>"
  }
}
```

---

### 9. Apply configuration

Use the `gateway` tool with `config.patch` action to add all the env vars at once:

```javascript
gateway({
  action: "config.patch",
  raw: JSON.stringify({
    env: {
      // Only include keys the user provided
      "LIMITLESS_API_KEY": "...",
      "FIREFLIES_API_KEY": "...",
      "QUO_API_KEY": "..."
    }
  })
})
```

### 10. Summary

Tell the user:
- ✅ What was installed
- ✅ Which skills are configured
- 📝 Remind them to personalize SOUL.md with their AI's personality
- 📝 Remind them to add info about themselves to USER.md and MEMORY.md

## Placeholders Reference

| Placeholder | Description |
|-------------|-------------|
| `{{USER_NAME}}` | The human's name |
| `{{ASSISTANT_NAME}}` | The AI assistant's name |
| `{{TIMEZONE}}` | User's timezone (e.g., America/Chicago) |
| `{{PRIORITY_1}}` | Top priority category |
| `{{PRIORITY_2}}` | Second priority category |

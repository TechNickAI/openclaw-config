# Setup Instructions

**For Clawdbot to follow when user asks to set up openclaw-config.**

## Prerequisites

- Clawdbot workspace exists (the directory you're operating in)
- Git available

## Steps

### 1. Clone the repo (if not already)

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

**Do NOT overwrite** if the file already exists and has been modified by the user.

### 3. Create memory folder structure

```bash
mkdir -p memory/people memory/projects memory/topics memory/decisions
```

### 4. Copy skills

Copy each folder from `~/.openclaw-config/skills/` to `workspace/skills/`:
- `limitless/`
- `fireflies/`
- `quo/`

### 5. Create MEMORY.md if it doesn't exist

```markdown
# MEMORY.md

## About {{USER_NAME}}

<!-- Add key info about yourself here -->

## Key People

<!-- One-liners about important people -->

## Active Projects

<!-- Pointers to memory/projects/ files -->

## Patterns & Preferences

<!-- What you've learned about the user -->
```

### 6. Track installation

Create `.openclaw/` in workspace:
```bash
mkdir -p .openclaw
```

Write version file:
```bash
cat ~/.openclaw-config/VERSION > .openclaw/installed-version
```

### 7. Prompt user to customize

Tell the user:
1. Edit `SOUL.md` to define your AI's personality
2. Edit `USER.md` to add your info
3. Search/replace `{{placeholders}}` in `AGENTS.md` with your values
4. Set API keys for any skills you want to use (LIMITLESS_API_KEY, FIREFLIES_API_KEY, QUO_API_KEY)

## Placeholders Reference

| Placeholder | What to replace with |
|-------------|---------------------|
| `{{USER_NAME}}` | The human's name |
| `{{ASSISTANT_NAME}}` | Your AI's name |
| `{{PRIORITY_1}}` | Top priority (e.g., "Work") |
| `{{PRIORITY_2}}` | Second priority (e.g., "Family") |
| `{{TIMEZONE}}` | Your timezone |

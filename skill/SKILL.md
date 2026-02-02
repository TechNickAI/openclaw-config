---
name: openclaw
description: Manage your openclaw-config installation - sync updates, check versions, add skills
triggers:
  - openclaw
  - config sync
  - update config
metadata:
  clawdbot:
    emoji: "🐾"
    requires:
      bins:
        - git
        - jq
---

# OpenClaw Config Management 🐾

Manage your openclaw-config installation from within Clawdbot.

## Quick Commands

```bash
# Check current version and if updates available
openclaw version
openclaw status

# Sync updates from upstream
openclaw sync

# Preview what would change
openclaw diff

# Force sync (overwrite local changes)
openclaw sync --force

# Add a skill from the repo
openclaw add-skill limitless

# Full upgrade with backup
openclaw upgrade
```

## Commands

### `openclaw version`
Show currently installed version.

### `openclaw status`
Check installed version vs. available remote version.

### `openclaw sync [--force] [--dry-run]`
Pull updates from the openclaw-config repository.
- Preserves files you've modified
- `--force` overwrites local changes
- `--dry-run` shows what would change

### `openclaw diff`
Show differences between your files and upstream.

### `openclaw add-skill <name>`
Add a specific skill from the repository.

### `openclaw upgrade`
Full upgrade: backup current config, pull latest, merge.

## How Sync Works

The sync system tracks which files you've modified:

1. **New upstream file** → Copies to your installation
2. **Unchanged locally** → Updates from upstream
3. **Modified locally** → Keeps your version, logs conflict
4. **With --force** → Overwrites with upstream version

Checksums are stored in `~/.openclaw/checksums.json`.

## Configuration

Set `CLAWDBOT_DIR` environment variable if your clawd directory isn't at `~/clawd`:

```bash
export CLAWDBOT_DIR=~/my-clawd
```

## Files

- `~/.openclaw/repo/` — Cached copy of openclaw-config repo
- `~/.openclaw/installed-version` — Your installed version
- `~/.openclaw/checksums.json` — File modification tracking
- `~/.openclaw/conflicts.log` — Last sync's conflicts

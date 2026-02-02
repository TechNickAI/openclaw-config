# Sync Instructions

**For OpenClaw to follow when user asks to sync/update openclaw-config.**

## Check for Updates

```bash
cd ~/.openclaw-config && git fetch
```

Compare local vs remote:
```bash
git log HEAD..origin/main --oneline
```

If no output, already up to date.

## Sync Process

### 1. Pull latest

```bash
cd ~/.openclaw-config && git pull
```

### 2. Check installed version

```bash
cat .openclaw/installed-version 2>/dev/null || echo "unknown"
```

Compare with:
```bash
cat ~/.openclaw-config/VERSION
```

### 3. Smart merge for templates

For each file in `~/.openclaw-config/templates/`:

**If file doesn't exist in workspace:**
→ Copy it

**If file exists and is IDENTICAL to the previous openclaw version:**
→ Safe to overwrite with new version

**If file exists and user has modified it:**
→ Keep user's version, but note what changed upstream

To detect user modifications, compare workspace file against the template.
If they differ significantly (beyond placeholder substitution), assume user modified it.

### 4. Update skills

For each skill in `~/.openclaw-config/skills/`:
- Copy/overwrite SKILL.md and CLI scripts
- Skills are generally safe to overwrite (no user customization expected)

### 5. Update installed version

```bash
cat ~/.openclaw-config/VERSION > .openclaw/installed-version
```

### 6. Report to user

Tell them:
- What version they're now on
- What files were updated
- What files were skipped (user modifications preserved)
- Any new features/changes from CHANGELOG.md

## Force Sync

If user explicitly asks to force/overwrite:
- Backup their current files to `.openclaw/backup/YYYY-MM-DD/`
- Overwrite everything from templates
- Still need to re-apply their placeholder values

## Show Diff

If user asks what would change:
- Compare each template file with workspace version
- Show meaningful differences (ignore placeholder substitutions)

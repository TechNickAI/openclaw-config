# Librarian to Cortex Migration Guide

Status: rollout pattern verified, updated after rollout correction | Date: 2026-04-19

## Purpose

This guide documents the migration from the deprecated `librarian` skill to `cortex`,
including the tested rollout process.

## Executive Summary

Librarian was a conversation-memory organizer that curated `memory/` and trimmed
`MEMORY.md`.

Cortex is a broader knowledge compiler. It owns:

- compiled knowledge storage
- memory routing/index maintenance
- ingest planning and state tracking
- linting and cross-link stitching
- learning analysis

This is not just a skill swap. It is a shift from local markdown curation to a unified
compiled knowledge system, with the root of `~/.openclaw/memory` as the source of truth.

## Architecture Shift

### Before: Librarian

Primary responsibilities:

- promote durable facts out of `memory/YYYY-MM-DD.md`
- update `memory/people/`, `projects/`, `topics/`, `decisions/`
- trim `MEMORY.md`
- maintain lightweight memory hygiene

Primary storage:

- local `memory/` tree inside the OpenClaw workspace

### After: Cortex

Primary responsibilities:

- maintain a dedicated knowledge store in Dropbox-backed storage
- compile raw sources into structured knowledge pages
- track ingest state in SQLite (`cortex.db`)
- maintain a thin memory routing layer for agent discovery
- replace librarian-triggered maintenance flows

Primary storage:

- the root of `~/.openclaw/memory/`
- optional Dropbox backup copied on a schedule to
  `~/Dropbox/Knowledge Base - <agentname>/`

## Important Design Decision

Do not reuse a shared `Knowledge Base` directory when multiple assistants exist.

The corrected configuration is:

- primary store: `~/.openclaw/memory/`
- backup target: `~/Dropbox/Knowledge Base - <agentname>/`

This avoids relying on a memory symlink pattern that was determined not to work well,
while still giving each assistant its own backup target.

## Current Cortex Behavior

The current Cortex v2 implementation:

- uses SQLite for ingest state
- does not require a `raw/` directory
- does not use lock files
- still contains a symlink-oriented `cortex link` flow in the CLI, but this rollout
  should not use it
- absorbs librarian functionality

## Machine Rollout Checklist

Use this sequence on each machine.

### 1. Update the repo

Pull latest `openclaw-config` and confirm:

- `skills/cortex/` exists
- `skills/librarian/` is marked deprecated
- docs reflect the current migration model

### 2. Choose the backup target name

Pick a unique Dropbox backup target per assistant.

Example:

- backup target directory: `Knowledge Base - <agentname>`

### 3. Use the local memory root as the primary store

Cortex content should live directly under:

```bash
~/.openclaw/memory/
```

Expected outcomes:

- `schema.md`, `cortex.db`, indexes, and content live directly in the memory root
- `MEMORY.md` stays alongside the Cortex files
- no symlink is involved

### 4. Create Cortex config

Before running any Cortex CLI commands, create `~/.config/cortex/config` so `scan`,
`triage`, `plan`, and `status` know where the local store lives.

Example:

```bash
mkdir -p ~/.config/cortex
printf '%s\n' \
  "CORTEX_STORE_PATH=$HOME/.openclaw/memory" \
  "CLOUD_PROVIDER=Dropbox" \
  "CORTEX_BACKUP_PATH=$HOME/Dropbox/Knowledge Base - <agentname>" \
  > ~/.config/cortex/config
```

### 5. Bulk discovery and ingest preparation

Example:

```bash
~/src/openclaw-config/skills/cortex/cortex scan ~/Dropbox
~/src/openclaw-config/skills/cortex/cortex triage
~/src/openclaw-config/skills/cortex/cortex plan
```

Do not run `cortex link` yet if bulk ingest is still pending.

### 6. Backup after ingest

When initial ingest is done, copy the local memory root to Dropbox:

```bash
rsync -a --delete ~/.openclaw/memory/ ~/Dropbox/"Knowledge Base - <agentname>"/
```

Expected outcomes:

- Dropbox receives a backup copy of the local memory root
- agents continue reading and writing locally in `~/.openclaw/memory`
- no symlink dependency exists in the runtime path

## Existing Data Policy

Do not perform a destructive migration of legacy memory files.

Preserve these as historical context:

- `memory/YYYY-MM-DD.md`
- `memory/people/`
- `memory/projects/`
- `memory/topics/`
- `memory/decisions/`
- `memory/learning/`

Going forward:

- new compiled knowledge belongs in Cortex
- `MEMORY.md` should become a routing layer, not the primary long-form store
- legacy librarian-style curation should phase out

## Writer and Reader Roles

Even without locking, operate Cortex as a single-writer system.

- **Writer machine**: allowed to run ingest, lint, rebuild-index, and structural updates
- **Reader machine**: reads linked knowledge, avoids structural writes

This prevents churn and accidental divergence.

## Verification Checklist

After rollout, verify all of the following:

- [ ] `~/.config/cortex/config` exists
- [ ] primary store exists directly in `~/.openclaw/memory/`
- [ ] Dropbox backup target exists
- [ ] `cortex.db` exists
- [ ] `schema.md` exists
- [ ] `cortex status` succeeds against the local memory root
- [ ] no runtime dependency on symlinked memory paths remains
- [ ] backup command copies local state to Dropbox successfully
- [ ] agent-facing docs describe the memory root as the source of truth

## Known Risks

### Split-brain memory

Operators may continue treating `memory/` as the primary long-term knowledge store.

Mitigation:

- document Cortex as the new source of truth for compiled knowledge
- keep `MEMORY.md` thin and pointer-oriented

### Namespace collisions

Multiple assistants sharing `Knowledge Base` causes confusion and ownership ambiguity.

Mitigation:

- use assistant-specific names like `Knowledge Base - <agentname>`

### Symlinked runtime storage

Using a symlinked runtime memory store proved unreliable in practice.

Mitigation:

- keep runtime state local under `~/.openclaw/memory`
- use Dropbox as backup only

### Doc drift

Older design docs may still describe superseded v1 behavior.

Mitigation:

- treat `skills/cortex/SKILL.md` and the CLI behavior as the operational source of truth
- update migration docs whenever rollout practice changes

## Rollout Notes

Rollout guidance was corrected after testing:

- symlinking the runtime memory store to Dropbox was not the right model
- the correct pattern is local primary storage under `~/.openclaw/memory`, with Dropbox
  backup every 3 hours

Recommended rollout pattern:

- local primary store: `~/.openclaw/memory/`
- Dropbox backup target: `~/Dropbox/Knowledge Base - <agentname>/`

This is the recommended pattern for future multi-assistant rollouts unless a stronger
storage model is introduced.

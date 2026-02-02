<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Config-D97757?style=for-the-badge" alt="OpenClaw Config">
</p>

# OpenClaw Config 🐾

Shareable configuration for [Clawdbot](https://github.com/clawdbot/clawdbot) — memory system, skills, and agent instructions.

## What This Is

A battle-tested configuration for running Clawdbot as a personal AI assistant:

- **Three-tier memory architecture** — Daily logs, curated long-term memory, and searchable deep knowledge
- **Decision-making frameworks** — Bezos's one-way/two-way doors, certainty thresholds, priority filters
- **Group chat behavior** — When to speak, when to stay silent, how to react like a human
- **Ready-to-use skills** — Limitless Pendant, Fireflies.ai, and Quo phone integrations

## Quick Start

**Just tell your Clawdbot:**

```
Set up openclaw-config from https://github.com/TechNickAI/openclaw-config

Clone the repo to ~/.openclaw-config, then follow SETUP.md to install
the templates and skills into my workspace.
```

That's it. Clawdbot reads SETUP.md and does the work.

## Updating

**Tell your Clawdbot:**

```
Sync my openclaw-config. Follow SYNC.md in ~/.openclaw-config.
```

The sync is smart — it preserves your customizations and only updates files you haven't modified.

## What's Included

### Templates

| File | Purpose |
|------|---------|
| `AGENTS.md` | Complete operating instructions (~400 lines of wisdom) |
| `SOUL.md` | AI personality and identity template |
| `USER.md` | Human profile template |
| `TOOLS.md` | Local environment notes |
| `HEARTBEAT.md` | Periodic check configuration |
| `IDENTITY.md` | Quick reference card |

### Memory Architecture

**Tier 1: Always-Loaded**
- `MEMORY.md` — ~100 lines max, curated essentials

**Tier 2: Daily Context**
- `memory/YYYY-MM-DD.md` — Today + yesterday's logs

**Tier 3: Deep Knowledge**
- `memory/people/`, `memory/projects/`, `memory/topics/`, `memory/decisions/`
- Searchable via RAG, loaded on-demand

### Skills

| Skill | Description | API Key |
|-------|-------------|---------|
| **limitless** | Limitless Pendant lifelogs | `LIMITLESS_API_KEY` |
| **fireflies** | Fireflies.ai meeting transcripts | `FIREFLIES_API_KEY` |
| **quo** | Quo business phone | `QUO_API_KEY` |

## After Setup

1. **Edit `SOUL.md`** — Define your AI's personality
2. **Edit `USER.md`** — Add your info  
3. **Replace placeholders** in `AGENTS.md`:

| Placeholder | Replace with |
|-------------|--------------|
| `{{USER_NAME}}` | Your name |
| `{{ASSISTANT_NAME}}` | Your AI's name |
| `{{PRIORITY_1}}` | Top priority (e.g., "Work") |
| `{{PRIORITY_2}}` | Second priority (e.g., "Family") |

4. **Set API keys** for skills you want to use

## The 4 Criteria for Memory Extraction

Built into AGENTS.md — your AI uses these to decide what to remember:

1. **Durability** — Will this matter in 30+ days?
2. **Uniqueness** — Is this new or already captured?
3. **Retrievability** — Will I want to recall this later?
4. **Authority** — Is this reliable?

## Philosophy

- **File-based memory** — Text files beat databases for AI context
- **Markdown over JSON** — Language models work better with prose
- **Two-way doors** — Act freely on reversible decisions; ask first on irreversible ones
- **Quality over quantity** — In groups, participate, don't dominate

## Contributing

PRs welcome! Keep templates generic (no personal/specific content).

## License

MIT

---

**Author:** [TechNickAI](https://github.com/TechNickAI)

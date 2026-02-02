<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Config-D97757?style=for-the-badge" alt="OpenClaw Config">
</p>

# OpenClaw Config 🐾

Shareable configuration for [OpenClaw](https://github.com/openclaw/openclaw) — memory system, skills, and agent instructions.

## What This Is

A battle-tested configuration for running OpenClaw as a personal AI assistant:

- **Three-tier memory architecture** — Daily logs, curated long-term memory, and searchable deep knowledge
- **Decision-making frameworks** — Bezos's one-way/two-way doors, certainty thresholds, priority filters
- **Group chat behavior** — When to speak, when to stay silent, how to react like a human
- **Ready-to-use skills** — Limitless Pendant, Fireflies.ai, and Quo phone integrations

## Quick Start

**Just tell your OpenClaw:**

```
Set up openclaw-config from https://github.com/TechNickAI/openclaw-config
```

OpenClaw will:
1. Clone the repo
2. Copy templates to your workspace
3. Ask for your name, AI's name, timezone, and priorities
4. Ask which skills you want and guide you through getting API keys
5. Configure everything automatically

No manual config editing. No environment variables to export.

## Updating

**Tell your OpenClaw:**

```
Sync my openclaw-config
```

It preserves your customizations and only updates files you haven't modified.

## What's Included

### Templates

| File | Purpose |
|------|---------|
| `AGENTS.md` | Complete operating instructions (~400 lines) |
| `SOUL.md` | AI personality template |
| `USER.md` | Human profile template |
| `TOOLS.md` | Local environment notes |
| `HEARTBEAT.md` | Periodic check config |
| `IDENTITY.md` | Quick reference card |

### Memory Architecture

**Tier 1: Always-Loaded**
- `MEMORY.md` — Curated essentials (~100 lines max)

**Tier 2: Daily Context**
- `memory/YYYY-MM-DD.md` — Today + yesterday's logs

**Tier 3: Deep Knowledge (RAG-searchable)**
- `memory/people/`, `memory/projects/`, `memory/topics/`, `memory/decisions/`

### Skills

| Skill | What it does |
|-------|--------------|
| **limitless** | Query Limitless Pendant lifelogs |
| **fireflies** | Search Fireflies.ai meeting transcripts |
| **quo** | Access Quo business phone calls & texts |

## The Memory Extraction Criteria

Your AI uses these to decide what to remember long-term:

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

PRs welcome! Keep templates generic (no personal content).

## License

MIT

---

**Author:** [TechNickAI](https://github.com/TechNickAI)

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Config-D97757?style=for-the-badge" alt="OpenClaw Config">
</p>

# OpenClaw Config 🐾

Shareable configuration for [OpenClaw](https://github.com/openclaw/openclaw) — memory system, skills, and agent instructions.

## What This Is

A battle-tested configuration for running OpenClaw as a personal AI assistant:

- **Three-tier memory architecture** — Daily logs, curated long-term memory, and searchable deep knowledge
- **Semantic memory search** — Vector embeddings via LM Studio (local, free) or OpenAI for finding relevant context
- **Decision-making frameworks** — Bezos's one-way/two-way doors, certainty thresholds, priority filters
- **Group chat behavior** — When to speak, when to stay silent, how to react like a human
- **Ready-to-use skills** — Limitless Pendant, Fireflies.ai, and Quo phone integrations

## Quick Start

```
Set up openclaw-config from https://github.com/TechNickAI/openclaw-config
```

## Updating

```
Update my openclaw config
```

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

**Tier 3: Deep Knowledge (Semantic Search)**
- `memory/people/`, `memory/projects/`, `memory/topics/`, `memory/decisions/`
- Indexed with vector embeddings for semantic similarity search
- Use `memory_search("query")` to find relevant context
- Supports LM Studio (local, recommended) or OpenAI for embeddings

### Skills

| Skill | What it does |
|-------|--------------|
| **limitless** | Query Limitless Pendant lifelogs |
| **fireflies** | Search Fireflies.ai meeting transcripts |
| **quo** | Access Quo business phone calls & texts |
| **parallel** | AI-optimized web search & content extraction (better than built-in) |

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

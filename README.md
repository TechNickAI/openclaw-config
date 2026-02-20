<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Config-D97757?style=for-the-badge&labelColor=1a1a2e" alt="OpenClaw Config">
  <br><br>
  <a href="https://github.com/TechNickAI/openclaw-config/releases"><img src="https://img.shields.io/badge/version-0.10.0-D97757?style=flat-square" alt="Version"></a>
  <img src="https://img.shields.io/badge/python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <a href="https://github.com/TechNickAI/openclaw-config/stargazers"><img src="https://img.shields.io/github/stars/TechNickAI/openclaw-config?style=flat-square&color=D97757" alt="Stars"></a>
  <img src="https://img.shields.io/badge/skills-9-blueviolet?style=flat-square" alt="Skills">
  <img src="https://img.shields.io/badge/workflows-2-blueviolet?style=flat-square" alt="Workflows">
  <a href="https://github.com/TechNickAI/openclaw-config/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome"></a>
</p>

<p align="center">
  <strong>Your AI's operating system.</strong><br>
  Memory, skills, workflows, and autonomous agents — all in markdown.
</p>

---

# OpenClaw Config

A battle-tested configuration for running your AI assistant the way it should be run —
with real memory, useful skills, and agents that work while you sleep.

This is what powers [OpenClaw](https://github.com/TechNickAI): a personal AI that
remembers everything, connects to your tools, and gets better over time.

## Highlights

- **Three-tier memory** — Daily logs, curated long-term memory, and semantic search
  across deep knowledge
- **9 skills** — From web research to meeting transcripts to CRM access, each a
  standalone UV script
- **Autonomous workflows** — Agents that run on a schedule, learn your preferences, and
  manage themselves
- **Decision frameworks** — Bezos's one-way/two-way doors, certainty thresholds,
  priority filters
- **DevOps built in** — Health checks, backup verification, and fleet management across
  machines

## Quick Start

Tell your OpenClaw instance:

```
Set up openclaw-config from https://github.com/TechNickAI/openclaw-config
```

To update later:

```
Update my openclaw config
```

That's it. Your AI handles the rest.

## Architecture

```
openclaw-config/
├── templates/          # Your AI's identity and operating instructions
│   ├── AGENTS.md       # Complete operating instructions
│   ├── SOUL.md         # AI personality definition
│   ├── USER.md         # Human profile
│   ├── MEMORY.md       # Curated essentials (~100 lines max)
│   ├── TOOLS.md        # Local environment config
│   ├── HEARTBEAT.md    # Periodic check schedule
│   └── IDENTITY.md     # Quick reference card
│
├── skills/             # Standalone UV scripts — no setup required
│   ├── asana/          # Task & project management
│   ├── fireflies/      # Meeting transcript search
│   ├── followupboss/   # Real estate CRM
│   ├── librarian/      # Knowledge base curation
│   ├── limitless/      # Pendant lifelog search
│   ├── openclaw/       # Self-management & updates
│   ├── parallel/       # Web research & extraction
│   ├── quo/            # Business phone & SMS
│   └── smart-delegation/ # Intelligent task routing
│
├── workflows/          # Autonomous agents with state & learning
│   ├── email-steward/  # Inbox triage & management
│   └── task-steward/   # Task classification & execution
│
├── memory/             # Example memory structure
│   ├── people/         # Relationship context
│   ├── projects/       # Project knowledge
│   ├── topics/         # Domain expertise
│   └── decisions/      # Decision history
│
└── devops/             # Health checks & fleet management
```

## Skills

Skills are standalone [UV scripts](https://docs.astral.sh/uv/guides/scripts/) — Python
with inline dependencies, no project setup required. Each skill is self-contained and
versioned independently.

| Skill                | What it does                                                                     | Version |
| -------------------- | -------------------------------------------------------------------------------- | ------- |
| **parallel**         | Web research & content extraction via Parallel.ai                                | 0.2.0   |
| **limitless**        | Query Limitless Pendant lifelogs & conversations                                 | 0.2.0   |
| **fireflies**        | Search Fireflies.ai meeting transcripts & action items                           | 0.2.0   |
| **quo**              | Business phone — calls, texts, transcripts, contacts                             | 0.2.0   |
| **asana**            | Task & project management — create, update, organize                             | 0.1.0   |
| **followupboss**     | Real estate CRM — contacts, deals, pipeline                                      | 0.1.0   |
| **librarian**        | Knowledge base curation — promotes, deduplicates, maintains                      | 0.1.0   |
| **smart-delegation** | Intelligent task routing — Opus for deep reasoning, Grok for unfiltered analysis | 0.1.0   |
| **openclaw**         | Self-management — setup, updates, health checks                                  | 0.2.2   |

## Workflows

Workflows are autonomous agents that run on a schedule. Unlike skills (tools you call),
workflows have state, learn your preferences over time, and manage themselves.

| Workflow          | What it does                                                           | Version |
| ----------------- | ---------------------------------------------------------------------- | ------- |
| **email-steward** | Inbox triage — archives debris, manages labels, alerts on important    | 0.2.0   |
| **task-steward**  | Task orchestration — classifies work, creates tasks, spawns sub-agents | 0.1.0   |

Each workflow maintains:

- `AGENT.md` — The algorithm (updates with openclaw-config)
- `rules.md` — Your preferences (you customize, never overwritten)
- `agent_notes.md` — Learned patterns (grows over time)
- `logs/` — Execution history

## Memory System

Your AI decides what to remember using four criteria:

| Criterion          | Question                          |
| ------------------ | --------------------------------- |
| **Durability**     | Will this matter in 30+ days?     |
| **Uniqueness**     | Is this new or already captured?  |
| **Retrievability** | Will I want to recall this later? |
| **Authority**      | Is this reliable?                 |

**Tier 1: Always-Loaded** — `MEMORY.md`, curated essentials in context at all times

**Tier 2: Daily Context** — `memory/YYYY-MM-DD.md`, today + yesterday loaded
automatically

**Tier 3: Deep Knowledge** — `memory/people/`, `projects/`, `topics/`, `decisions/`,
indexed with vector embeddings for semantic search. Supports LM Studio (local, free) or
OpenAI.

## Philosophy

- **File-based memory** — Text files beat databases for AI context
- **Markdown over JSON** — Language models think better in prose
- **Two-way doors** — Act freely on reversible decisions; pause on irreversible ones
- **Self-contained skills** — No shared dependencies, no coordination overhead
- **Workflows that learn** — Agents should get better at their job, not just repeat it

## Development

```bash
# Run tests
uv run --with pytest pytest tests/ -v
```

Integration tests auto-skip when API keys aren't set.

## Contributing

PRs welcome! Keep templates generic (no personal content). Each skill should remain
self-contained with its own inline dependencies.

## License

MIT

---

<p align="center">
  Built by <a href="https://github.com/TechNickAI">TechNickAI</a><br>
  <sub>Your AI deserves an operating system.</sub>
</p>

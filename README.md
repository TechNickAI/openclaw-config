<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Config-D97757?style=for-the-badge" alt="OpenClaw Config">
</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/Quick_Start-blue" alt="Quick Start"></a>
  <a href="#whats-included"><img src="https://img.shields.io/badge/What's_Included-green" alt="What's Included"></a>
  <a href="#skills"><img src="https://img.shields.io/badge/Skills-orange" alt="Skills"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="MIT License"></a>
</p>

# OpenClaw Config 🐾

Shareable configuration for [OpenClaw](https://github.com/openclaw/openclaw) — memory system, skills, task tracking, and agent instructions.

## What This Is

A battle-tested configuration for running OpenClaw as a personal AI assistant. This repo provides:

- **Three-tier memory architecture** — Daily logs, curated long-term memory, and searchable deep knowledge
- **Decision-making frameworks** — Bezos's one-way/two-way doors, certainty thresholds, priority filters
- **Task tracking system** — GitHub-style checkboxes with priorities, blocking states, and heartbeat reminders
- **Group chat behavior** — When to speak, when to stay silent, how to react like a human
- **Ready-to-use skills** — Limitless Pendant, Fireflies.ai, and Quo phone integrations

## Quick Start

```bash
# Set your openclaw directory (if not ~/openclaw)
export OPENCLAW_DIR=~/openclaw

# Run bootstrap
curl -fsSL https://raw.githubusercontent.com/TechNickAI/openclaw-config/main/scripts/bootstrap.sh | bash
```

Then customize your installation:
1. Edit `SOUL.md` — Define your AI's personality
2. Edit `USER.md` — Add your info
3. Search/replace `{{placeholders}}` in `AGENTS.md`
4. Configure API keys for skills you want to use

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

### Memory System

```
memory/
├── TASK-SYSTEM.md        # Task tracking protocol
├── tasks.md              # Active tasks
├── heartbeat-state.json  # Check timing state
├── people/               # Context about individuals
├── projects/             # Project knowledge
├── topics/               # Domain knowledge
└── decisions/            # Significant choices made
```

### Skills

| Skill | Description |
|-------|-------------|
| **limitless** | Limitless Pendant lifelogs — search and query your conversations |
| **fireflies** | Fireflies.ai meeting transcripts — summaries, action items, full transcripts |
| **quo** | Quo business phone — calls, texts, contacts, call transcripts |
| **openclaw** | Meta-skill for managing this config |

## Memory Architecture

The config implements a three-tier memory system:

**Tier 1: Always-Loaded (Profile)**
- `MEMORY.md` — ~100 lines max, curated essentials
- Loaded every session

**Tier 2: Daily Context (Session State)**
- `memory/YYYY-MM-DD.md` — Today + yesterday
- Raw logs, everything that happened

**Tier 3: Deep Knowledge (Searchable)**
- `memory/people/`, `memory/projects/`, `memory/topics/`, `memory/decisions/`
- Retrieved on-demand, not loaded by default

### The 4 Criteria for Memory Extraction

1. **Durability** — Will this matter in 30+ days?
2. **Uniqueness** — Is this new or already captured?
3. **Retrievability** — Will I want to recall this later?
4. **Authority** — Is this reliable?

## Sync & Updates

The config includes a smart sync system that preserves your customizations:

```bash
# Check for updates
openclaw status

# Preview what would change
openclaw diff

# Sync updates (preserves your modifications)
openclaw sync

# Force update (overwrites local changes)
openclaw sync --force
```

**How sync works:**
- New files upstream → Copied to your installation
- You haven't modified → Updated from upstream
- You have modified → Your version kept, conflict logged
- With `--force` → Upstream overwrites everything

## Skills Setup

### Limitless Pendant
```bash
export LIMITLESS_API_KEY=your-key  # From app.limitless.ai → Settings → Developer

limitless recent 5
limitless search "meeting with john"
limitless today
```

### Fireflies.ai
```bash
export FIREFLIES_API_KEY=your-key  # From app.fireflies.ai → Integrations → API

fireflies recent 5
fireflies search "product roadmap"
fireflies get <transcript-id>
```

### Quo (Business Phone)
```bash
export QUO_API_KEY=your-key  # From my.quo.com → Settings → API

quo numbers
quo conversations
quo transcript <call-id>
```

## Contributing

### Adding Skills

1. Create `skills/your-skill/SKILL.md` with frontmatter
2. Create `skills/your-skill/your-skill` CLI script
3. Document environment variables needed
4. Submit a PR!

### Improving Templates

The templates are generic by design. Improvements welcome, but avoid adding personal/specific content.

## Placeholder Reference

Templates use these placeholders — search/replace with your values:

| Placeholder | Description |
|-------------|-------------|
| `{{USER_NAME}}` | The human's name |
| `{{ASSISTANT_NAME}}` | Your AI assistant's name |
| `{{PRIORITY_1}}` | Top priority category |
| `{{PRIORITY_2}}` | Second priority category |
| `{{TIMEZONE}}` | Your timezone |
| `{{PRIMARY_CHANNEL}}` | Main communication channel |

## Philosophy

- **File-based memory** — Text files beat databases for AI context
- **Markdown over JSON** — You're a language model, not a data processor
- **Two-way doors** — Act, then inform. One-way doors: ask first.
- **Quality over quantity** — In groups, participate, don't dominate
- **Proactive, not annoying** — Check in a few times a day, respect quiet time

## License

MIT — Use it, modify it, share it.

---

**Author:** [TechNickAI](https://github.com/TechNickAI)  
**Repository:** https://github.com/TechNickAI/openclaw-config

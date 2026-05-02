<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Config-D97757?style=for-the-badge&labelColor=1a1a2e" alt="OpenClaw Config">
  <br><br>
  <img src="https://img.shields.io/badge/python-3.13+-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python 3.13+">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <a href="https://github.com/TechNickAI/openclaw-config/stargazers"><img src="https://img.shields.io/github/stars/TechNickAI/openclaw-config?style=flat-square&color=D97757" alt="Stars"></a>
  <a href="https://github.com/TechNickAI/openclaw-config/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square" alt="PRs Welcome"></a>
</p>

<p align="center">
  <strong>Give your AI assistant memory, skills, and autonomy.</strong><br>
  A shareable config that turns Claude Code into an AI that remembers you,<br>
  connects to your tools, and runs workflows while you sleep.
</p>

---

# OpenClaw Config

Most AI assistants forget you the moment the conversation ends. OpenClaw doesn't.

This repo is the shared configuration layer for OpenClaw — a personal AI built on
[Claude Code](https://docs.anthropic.com/en/docs/claude-code) that maintains persistent
memory, integrates with real-world tools, and runs autonomous workflows on a schedule.
Everything is markdown and Python scripts. No frameworks, no databases, no lock-in.

## What You Get

- **Memory that persists** — Three-tier architecture: always-loaded essentials, daily
  context files, and deep knowledge with semantic search
- **Skills** — Web research, meeting transcripts, CRM, phone system, voice calling, task
  management, and more — each a standalone Python script with zero setup
- **Autonomous workflows** — Agents that triage your inbox, manage tasks, prep your
  calendar, organize contacts, monitor security threats, keep cron jobs healthy, and
  improve themselves over time — learning your preferences and compounding corrections
  into permanent knowledge
- **Templates for identity** — Define your AI's personality, your profile, and how it
  should operate
- **DevOps included** — Hourly health checks, fleet management across machines,
  automated backups

## Getting Started

**Prerequisites:** [Claude Code](https://docs.anthropic.com/en/docs/claude-code) running
on your machine. That's it — no other dependencies.

**Install:** Open Claude Code and tell it:

```
Set up openclaw-config from https://github.com/TechNickAI/openclaw-config
```

The `openclaw` skill walks you through setup — cloning the repo, copying templates,
creating memory folders, and configuring optional features like semantic search.

**Update later:**

```
Update my openclaw config
```

## How It's Organized

```
openclaw-config/
├── templates/          # Identity & operating instructions
│   ├── AGENTS.md       # How the AI should think and act
│   ├── SOUL.md         # Personality definition (templated)
│   ├── USER.md         # Your profile — who you are, how you work
│   ├── MEMORY.md       # Curated essentials, always in context
│   ├── BOOT.md         # Startup routine — what to check on launch
│   ├── HEARTBEAT.md    # Periodic checks (inbox, tasks, health)
│   ├── TOOLS.md        # Machine-specific environment config
│   └── IDENTITY.md     # Quick reference card
│
├── skills/             # Standalone UV scripts — no install needed
│   ├── parallel/       # Web research & content extraction
│   ├── quo/            # Business phone — calls, texts, contacts
│   ├── fathom/         # Meeting recording & transcript search
│   ├── fireflies/      # Meeting transcript search
│   ├── limitless/      # Pendant lifelog search
│   ├── asana/          # Task & project management (Asana)
│   ├── todoist/        # Task & project management (Todoist)
│   ├── followupboss/   # Real estate CRM
│   ├── cortex/         # Personal knowledge compiler
│   ├── librarian/      # Deprecated → replaced by cortex
│   ├── create-great-prompts/  # Prompt engineering guide
│   ├── smart-delegation/     # Route work to the right model
│   ├── vapi-calls/          # Voice calls via Vapi AI
│   ├── workflow-builder/     # Design new autonomous workflows
│   └── openclaw/       # Self-management & updates
│
├── workflows/          # Autonomous agents with state & learning
│   ├── email-steward/  # Inbox triage — archive noise, surface what matters
│   ├── task-steward/   # Classify, create, execute, and QA tasks
│   ├── calendar-steward/    # Daily briefing with travel & meeting prep
│   ├── contact-steward/    # Detect and organize unknown contacts
│   ├── security-sentinel/  # Threat intelligence & exposure mapping
│   ├── cron-healthcheck/   # Broken cron detection & auto-remediation
│   └── learning-loop/     # Self-improvement — corrections → patterns → knowledge
│
├── memory/             # Example memory directory structure
│   ├── people/         # One file per person
│   ├── projects/       # One file per project
│   ├── topics/         # Domain expertise & preferences
│   ├── decisions/      # Important decisions with reasoning
│   └── learning/       # Corrections, patterns, and improvement archive
│
└── devops/             # Health checks & fleet management
```

## Skills

Each skill is a standalone [UV script](https://docs.astral.sh/uv/guides/scripts/) —
Python with inline dependencies, no project-level setup. Run directly, version
independently.

| Skill                    | What it does                                                           | Version |
| ------------------------ | ---------------------------------------------------------------------- | ------- |
| **parallel**             | Web search, extraction, deep research & enrichment via Parallel.ai CLI | 0.3.0   |
| **quo**                  | Business phone — calls, texts, voicemails, contacts, SMS               | 0.6.0   |
| **fathom**               | Query meeting recordings — transcripts, summaries, action items        | 0.1.0   |
| **fireflies**            | Search meeting transcripts & action items                              | 0.2.0   |
| **limitless**            | Query Pendant lifelogs & conversations                                 | 0.2.0   |
| **asana**                | Task & project management via MCP                                      | 0.1.0   |
| **todoist**              | Task & project management via official CLI                             | 0.1.0   |
| **followupboss**         | Real estate CRM — contacts, deals, pipeline                            | 0.1.0   |
| **hubspot**              | HubSpot CRM — contacts, deals, and deal pipelines                      | 0.1.0   |
| **librarian**            | ~~Knowledge base maintenance~~ → replaced by **cortex**                | 0.5.0   |
| **create-great-prompts** | Prompt engineering for LLM agents                                      | 2.0.0   |
| **smart-delegation**     | Route work to Opus, Grok, or handle directly                           | 0.2.0   |
| **workflow-builder**     | Design new autonomous workflows                                        | 0.1.0   |
| **gateway-restart**      | Graceful gateway restart — waits for active work                       | 0.1.0   |
| **vapi-calls**           | Make outbound phone calls via Vapi voice AI                            | 0.1.0   |
| **tgcli**                | Read, search, and send Telegram messages via personal account          | 0.1.0   |
| **cortex**               | Personal knowledge compiler — ingest, query, lint, memory maintenance  | 0.2.0   |
| **review**               | Pause before sending — empathy-first multi-lens review of artifacts    | 0.2.0   |
| **openclaw**             | Install, update, and health-check the config                           | 0.2.2   |

## Workflows

Workflows are autonomous agents that run on a schedule. Unlike skills (tools you
invoke), workflows maintain state, learn your preferences, and manage themselves.

| Workflow              | What it does                                                               | Version |
| --------------------- | -------------------------------------------------------------------------- | ------- |
| **email-steward**     | Triage inbox — archive noise, label, alert on important                    | 0.3.0   |
| **task-steward**      | Classify work, create tasks, spawn sub-agents, QA results                  | 0.1.0   |
| **calendar-steward**  | Daily briefing — travel time, meeting prep, conflict detection             | 0.1.0   |
| **contact-steward**   | Detect unknown contacts across platforms, classify & organize              | 0.2.2   |
| **security-sentinel** | Threat intelligence research & fleet exposure mapping                      | 0.1.0   |
| **cron-healthcheck**  | Detect broken cron jobs, auto-remediate, escalate failures                 | 0.1.0   |
| **learning-loop**     | Self-improvement — capture corrections, detect patterns, promote learnings | 0.1.0   |
| **llm-usage-report**  | Daily LLM spend digest — cost breakdown by session and model               | 0.1.0   |

Each workflow maintains its own state:

- `AGENT.md` — The algorithm (updates when you update openclaw-config)
- `rules.md` — Your preferences (never overwritten)
- `agent_notes.md` — Patterns it learns over time
- `logs/` — Execution history

## Memory Architecture

Most AI memory is "dump everything into a vector database." OpenClaw uses deliberate,
structured memory with clear tiers:

**Tier 1 — Always loaded.** `MEMORY.md` stays in context every conversation. Curated to
~100 lines of what matters most.

**Tier 2 — Daily context.** `memory/YYYY-MM-DD.md` files. Today and yesterday load
automatically. Raw observations, not curated.

**Tier 3 — Deep knowledge.** `memory/people/`, `projects/`, `topics/`, `decisions/`.
Searched via vector embeddings (LM Studio local or OpenAI). Retrieved when relevant, not
loaded by default.

The **cortex** skill compiles raw sources into structured knowledge — documents, notes,
and transcripts become interlinked entity pages, summaries, and decision records.

What gets remembered is filtered through four criteria:

| Criterion          | Question                          |
| ------------------ | --------------------------------- |
| **Durability**     | Will this matter in 30+ days?     |
| **Uniqueness**     | Is this new or already captured?  |
| **Retrievability** | Will I want to recall this later? |
| **Authority**      | Is this reliable?                 |

## Design Principles

- **Files over databases** — Markdown in git beats any proprietary store. Readable,
  diffable, portable.
- **Self-contained skills** — No shared dependencies, no coordination overhead. Each
  skill carries its own `pip install` inline.
- **Workflows that learn** — Agents should get better at their job over time, not just
  repeat the same script.
- **Two-way door decisions** — Act freely on reversible decisions. Pause and confirm on
  irreversible ones.
- **Prose over config** — Language models reason better in natural language than in JSON
  schemas.

## DevOps

Infrastructure-as-code for running OpenClaw in production. Supports macOS (launchd) and
Linux (systemd) with the same operational model.

### Health Monitoring

`devops/health-check.md` is an autonomous agent that runs every 30 minutes via cron. It
checks gateway liveness, model catalog health, cron job status, channel connectivity,
disk/memory, and log health. It can fix routine issues (restart services, kill hung
processes, clean old logs) and escalates to the fleet owner when things break that were
working.

Health checks follow a **silent success** model — the admin only gets notified when
something is wrong or was fixed, never for routine health.

### Machine Setup

Desired-state specifications that define what a healthy OpenClaw machine looks like:

| File                            | Platform | What it covers                                      |
| ------------------------------- | -------- | --------------------------------------------------- |
| `devops/machine-setup.md`       | macOS    | Power management, Node, launchd services, backups   |
| `devops/machine-setup-linux.md` | Linux    | EC2 setup, systemd services, SSH, package deps      |
| `devops/apt-packages.txt`       | Linux    | Required packages (jq, restic, tmux, git, bat, etc) |

Each section follows the pattern: **desired state** → **verify command** → **fix
command**. The health check agent uses these specs for drift detection.

### Security Hardening

`devops/machine-security-review.md` is a security-focused agent that runs daily (drift
detection) and weekly (full audit + red team). It checks firewall config, open ports,
file permissions, SSH hardening, credential exposure, prompt injection in memory/agent
files, skill script integrity, and MCP tool poisoning. It can auto-fix safe issues
(permission tightening) and escalates everything else to the fleet admin.

The companion `workflows/security-sentinel/` researches emerging AI security threats
weekly and maps them against the fleet's exposure.

### Notification Routing

`devops/notification-routing.md` defines a two-lane model:

- **Admin lane** — System health alerts go to the fleet owner (e.g., "gateway down on
  machine-2")
- **User lane** — Cron outputs go to the host person (e.g., EOD briefing, email alerts)

Lanes never mix. Health check agents use `delivery.mode: "none"` and self-notify the
admin directly.

### Automation Services

Three services run on every OpenClaw machine, defined as launchd plists (`devops/mac/`)
or systemd units (`devops/linux/`):

| Service              | Schedule         | Purpose                                                       |
| -------------------- | ---------------- | ------------------------------------------------------------- |
| **health-check**     | Every 30 min     | Run health-check.md agent via Claude CLI                      |
| **workspace-backup** | Every 4 hours    | Restic backup of ~/.openclaw + workspace (7d/4w/6m retention) |
| **backup-verify**    | Weekly (Sun 4am) | Restic integrity check (10% of data)                          |

### App Router

`devops/app-router/` is a per-machine pattern for hosting named web apps behind a single
Tailscale HTTPS URL with optional per-app password protection. Caddy fronts PM2-managed
processes; an Express auth sidecar issues path-scoped session cookies via Caddy's
`forward_auth`. See `devops/app-router/README.md` for setup; `install.sh` automates the
copy/sed/launchd-bootstrap dance.

### Fleet Management

For multi-machine deployments, the `/fleet` command manages remote OpenClaw instances
from a master machine. Fleet state lives in `~/openclaw-fleet/` (one markdown file per
server). The `gateway-restart` skill ensures graceful restarts that don't interrupt
active conversations.

## Documentation

Deep-dive guides for advanced setups and multi-agent coordination:

| Document                                   | Purpose                                                                               |
| ------------------------------------------ | ------------------------------------------------------------------------------------- |
| **knowledge/multi-agent-communication.md** | Setup multi-agent coordination across separate OpenClaw gateways via Slack @-mentions |
| **knowledge/fleet-boot-patterns.md**       | Complete runbook for booting, scaling, and managing a fleet of 3+ agents              |

### Multi-Agent Coordination

If you're running multiple OpenClaw instances that need to coordinate:

- **Single-gateway multi-agent:** Fast in-process communication via `sessions_send()`
- **Multi-gateway fleet:** Isolated agents across machines/VPS, coordinating via Slack

Both patterns are documented with working configs, troubleshooting guides, and boot
runbooks.

## Development

```bash
uv run --with pytest pytest tests/ -v
```

Integration tests auto-skip when API keys aren't set.

## Contributing

PRs welcome. Keep templates generic (no personal content). Each skill should remain
self-contained with its own inline dependencies.

## License

MIT

---

<p align="center">
  Built by <a href="https://github.com/TechNickAI">TechNickAI</a><br>
  <sub>Your AI deserves to remember you.</sub>
</p>

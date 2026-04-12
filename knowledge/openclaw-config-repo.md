# OpenClaw Config Repository

Complete inventory of what this repository (`openclaw-config`) provides — the shareable
configuration layer for OpenClaw instances.

**Last updated:** 2026-04-09

---

## What This Repo Is

This is the **upstream source** for all OpenClaw instances. It contains the templates,
skills, workflows, devops specs, and knowledge that get deployed to live instances. It
is NOT the OpenClaw gateway code itself — it's the configuration and tooling layer.

**Deployment model:** The `openclaw` skill copies files from this repo to a live
instance's workspace (`~/.openclaw/workspace/`). Upstream-owned files (algorithms,
templates, skills) are overwritten on update. User-owned files (rules, notes, logs) are
never touched.

**Public repo:** This is open-source and intended to be shareable. Zero PII, zero fleet
specifics. Generic placeholders in all examples.

---

## Repository Structure

```
openclaw-config/
├── skills/              Standalone tools (Python UV scripts + bash wrappers)
├── workflows/           Autonomous agents with state and learning
├── templates/           Identity and deployment templates
├── devops/               Health check, machine setup, security review, notifications
├── knowledge/            Operational documentation and architecture guides
├── memory/               Example memory structure (people/, projects/, topics/)
├── tests/                pytest suite for workflows and skill integrations
├── .claude/
│   ├── commands/         Claude Code slash commands (fleet, update-model, fleet-announce)
│   └── settings.json     Hooks and plugin configuration
├── AGENTS.md             Project instructions (CLAUDE.md is a symlink to this)
├── CHANGELOG.md          Version history
├── VERSION               Current version number
└── README.md             Overview and getting started
```

---

## Skills

Each skill is self-contained: `SKILL.md` (metadata) + executable script (same name as
directory). No shared code, no project-level dependencies.

### Communication Skills

| Skill      | Version | What It Does                                                     | Dependencies                    |
| ---------- | ------- | ---------------------------------------------------------------- | ------------------------------- |
| agentmail  | 0.1.0   | Email inboxes for AI agents — create addresses, send/receive     | AGENTMAIL_API_KEY               |
| quo        | 0.6.0   | Business phone via OpenPhone — calls, texts, contacts, voicemail | (configured in OpenPhone)       |
| tgcli      | 0.1.0   | Read/send Telegram messages via CLI                              | Telegram bot token              |
| vapi-calls | 0.1.0   | Outbound phone calls via Vapi voice AI                           | VAPI_API_KEY, VAPI_ASSISTANT_ID |

### Knowledge & Research Skills

| Skill     | Version | What It Does                                          | Dependencies       |
| --------- | ------- | ----------------------------------------------------- | ------------------ |
| parallel  | 0.3.0   | Web search, content extraction, data enrichment       | PARALLEL_API_KEY   |
| limitless | 0.2.0   | Query Limitless Pendant lifelogs                      | LIMITLESS_API_KEY  |
| fireflies | 0.2.0   | Search Fireflies.ai meeting transcripts               | FIREFLIES_API_KEY  |
| fathom    | 0.1.0   | Query Fathom AI meeting recordings                    | FATHOM_API_KEY     |
| librarian | 0.3.0   | Knowledge base maintenance — curate, promote, archive | (no external deps) |

### Productivity Skills

| Skill        | Version | What It Does                                     | Dependencies       |
| ------------ | ------- | ------------------------------------------------ | ------------------ |
| asana        | 0.1.0   | Manage Asana tasks, projects, workspaces via MCP | ASANA_ACCESS_TOKEN |
| todoist      | 0.1.0   | Manage Todoist tasks via CLI                     | TODOIST_API_TOKEN  |
| followupboss | 0.1.0   | Query/manage Follow Up Boss CRM                  | FUB_API_KEY        |

### Meta Skills

| Skill                | Version | What It Does                                    | Dependencies       |
| -------------------- | ------- | ----------------------------------------------- | ------------------ |
| openclaw             | 0.3.0   | Install, configure, update openclaw-config      | (no external deps) |
| gateway-restart      | 0.1.0   | Graceful gateway restart with zero message loss | (no external deps) |
| smart-delegation     | 0.2.0   | Route tasks to optimal model (cost/capability)  | (no external deps) |
| workflow-builder     | 0.2.0   | Design and build autonomous workflows           | (no external deps) |
| create-great-prompts | 2.0.0   | Prompt engineering methodology guide            | (no external deps) |

### Skill Architecture

- **Python skills:** Use `uv run` with inline `# /// script` dependencies — no
  pyproject.toml, no virtualenv setup needed
- **Bash skills:** Thin wrappers around external CLIs
- **Meta skills:** SKILL.md only (instructions/methodology, no executable)
- **Testing:** Integration tests in `tests/` auto-skip without API keys

---

## Workflows

Autonomous agents that run on schedules, maintain state, and learn from corrections.

### Active Workflows

| Workflow          | What It Does                                                                                | Key Files                                |
| ----------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------- |
| email-steward     | Inbox triage — archive noise, surface important mail. Prompt injection defenses.            | AGENT.md                                 |
| task-steward      | Classify work, create tasks, execute via sub-agents, QA verification.                       | AGENT.md                                 |
| calendar-steward  | Daily briefing with travel logistics, meeting prep, conflict detection.                     | AGENT.md                                 |
| contact-steward   | Detect unknown contacts across WhatsApp/iMessage/Quo, classify, organize.                   | AGENT.md, classifier.md, platforms/\*.md |
| cron-healthcheck  | Detect broken cron jobs, auto-remediate common issues. Two-tier model (triage + diagnosis). | AGENT.md, agent_notes.md                 |
| learning-loop     | Capture corrections → detect patterns → validate → promote to memory.                       | AGENT.md, agent_notes.md, rules.md       |
| llm-usage-report  | Daily LLM spend breakdown by session and model. Empathy pass for tone.                      | AGENT.md, agent_notes.md, logs/          |
| security-sentinel | Research AI security threats, map to OpenClaw architecture, verify fleet exposure via SSH.  | AGENT.md, agent_notes.md                 |
| mailroom-steward  | Advanced email routing (not yet implemented — directory exists with logs/ only).            | —                                        |

### Workflow File Ownership

**Upstream-owned** (updated by this repo):

- `AGENT.md` — the algorithm definition
- `classifier.md` — classification logic (where applicable)
- `platforms/*.md` — platform-specific guides

**User-owned** (never overwritten):

- `rules.md` — user preferences and thresholds
- `agent_notes.md` — learned patterns (accumulated over time)
- `preferences.md` — user-specific settings
- `processed.md` — tracking what's been handled
- `logs/` — execution history

### Workflow Architecture

- Each workflow is a prompt + context that runs via the cron runner
- State persists in markdown files between runs
- `agent_notes.md` accumulates over time — workflows get smarter
- Corrections feed into `learning-loop`, which promotes patterns back to workflows
- Workflows can invoke skills (e.g., email-steward uses agentmail)

---

## Templates

Identity and configuration files deployed to `~/.openclaw/workspace/`:

| Template     | Purpose                                                     | Typical Size       |
| ------------ | ----------------------------------------------------------- | ------------------ |
| AGENTS.md    | Workspace definition — how the AI should think and act      | ~17K chars         |
| SOUL.md      | Personality — essence, name, communication style            | Varies by instance |
| USER.md      | User profile — who the human is, preferences, working style | Varies             |
| MEMORY.md    | Curated essentials, always loaded into context              | ~100 lines         |
| BOOT.md      | Startup routine — conversation recovery, pre-checks         | Short              |
| HEARTBEAT.md | Periodic checks — inbox, tasks, health (rotated daily)      | Medium             |
| TOOLS.md     | Machine-specific environment config and notes               | Short              |
| IDENTITY.md  | Quick reference card (one-page identity summary)            | Short              |

**Also:** `multi-agent-slack-bus.json` — configuration template for multi-agent
coordination via Slack.

---

## DevOps

Infrastructure management specs for fleet machines:

### health-check.md

- Runs every 30 minutes via cron
- Checks: gateway liveness, model catalog, cron job health, disk/memory, log health
- Auto-fixes: restarts, hung processes, old logs
- Escalates: failures to admin via Telegram
- Silent success model — only notifies on problems

### machine-setup.md (macOS)

Desired-state specification covering:

- Power management (prevent sleep)
- Permissions, Brewfile, Node.js setup
- Gateway config and service installation
- Automated backup with retention
- Workspace structure and agent defaults
- Health check admin notification setup

### machine-setup-linux.md

Linux-specific setup:

- Tailscale, SSH hardening
- System packages, Node.js, pnpm
- Gateway config with systemd
- Backup with systemd timers
- Whisper.cpp for voice transcription

### machine-security-review.md

Two-mode security agent:

- **Drift detection** (daily) — fast check for changes since baseline
- **Full audit + red team** (weekly) — comprehensive review including adversarial
  testing
- Checks: firewall, open ports, file permissions, SSH config, API key exposure, cron
  integrity, prompt injection, skill script integrity
- Auto-fixes safe issues, escalates everything else

### notification-routing.md

Two-lane notification model:

- **Lane 1 (Admin):** System health alerts to fleet admin via Telegram
- **Lane 2 (User):** Cron outputs to the instance's host person
- Per-machine configuration in `~/.openclaw/health-check-admin`

---

## Commands (.claude/commands/)

Claude Code slash commands for fleet operations:

| Command           | Purpose                                                                        |
| ----------------- | ------------------------------------------------------------------------------ |
| fleet.md          | Multi-machine deployment — assess state, push updates, coordinate across fleet |
| update-model.md   | Change OpenClaw model config with 5-point verification                         |
| fleet-announce.md | Send personalized announcements to fleet users                                 |

These commands run from the fleet master machine (this repo) and operate on remote
machines via SSH.

---

## Knowledge Base

Operational documentation in `knowledge/`:

| Document                        | What It Covers                                                      |
| ------------------------------- | ------------------------------------------------------------------- |
| model-aliases.md                | Role-based model aliases, cost/EQ benchmarks, subscriber overlays   |
| model-configs-and-jobs.md       | Model selection, provider routing, fallback chains, cron scheduling |
| fleet-boot-patterns.md          | Multi-agent coordination, session persistence, loop detection       |
| multi-agent-communication.md    | Cross-gateway agent coordination via Slack                          |
| fleet-boot-patterns-research.md | Deep research on bootstrapping, deployment, persistence             |
| plans/vapi-phone-skill.md       | Design brainstorm for Vapi voice call capability                    |

---

## Testing

pytest-based testing with auto-skip for integration tests:

```bash
uv run --with pytest pytest tests/ -v
```

### Test Coverage

**Workflow structure tests:** Validate AGENT.md frontmatter and required sections for
llm-usage-report workflow.

**Skill integration tests:** agentmail, fireflies, fathom, limitless, parallel, quo,
followupboss — all auto-skip without respective API keys.

**Skill wrapper tests:** Verify bash/uv wrappers around external CLIs function
correctly.

---

## What This Repo Provides (Summary)

This repo is the **shareable brain** for OpenClaw instances:

1. **Integration skills** — API wrappers for communication, knowledge, productivity
2. **Autonomous workflows** — scheduled agents that learn and maintain state
3. **Identity templates** — personality, preferences, startup routines
4. **DevOps specs** — health monitoring, machine setup, security hardening
5. **Fleet commands** — multi-machine management from Claude Code
6. **Knowledge docs** — model routing, multi-agent patterns, boot sequences
7. **Test suite** — validation for workflows and skill integrations

**What it does NOT contain:**

- The OpenClaw gateway source code (separate private repository)
- Fleet-specific data (that's in `~/openclaw-fleet/`, private)
- Instance-specific configuration (that's in `~/.openclaw/`, per-machine)
- API keys or credentials (all referenced via environment variables)

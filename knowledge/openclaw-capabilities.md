# OpenClaw Capabilities

Complete inventory of what OpenClaw provides as a platform. Written to support migration
analysis — what would need to be replicated if moving away from the OpenClaw gateway.

**Last updated:** 2026-04-09

---

## Architecture

OpenClaw is a **persistent AI gateway** — a Node.js daemon that runs 24/7 as a system
service (launchd on macOS, systemd on Linux). It:

- Stays running across reboots (managed by the OS service layer)
- Accepts messages from multiple channels simultaneously
- Maintains persistent state (memory, sessions, workflow progress)
- Executes scheduled jobs via a built-in cron runner
- Routes requests to LLM providers with fallback chains

The gateway binds to a local port (default 18789) and exposes a web dashboard for
monitoring. It's a single binary installed via npm.

**Key architectural property:** OpenClaw is always on. It doesn't need a human to start
a session. Messages arrive, cron jobs fire, health checks run — all without interaction.

---

## Messaging Channels

OpenClaw connects to messaging platforms via persistent adapters:

| Channel  | Transport                 | Auth                              | Notes                                                  |
| -------- | ------------------------- | --------------------------------- | ------------------------------------------------------ |
| WhatsApp | WebSocket (linked device) | QR code pairing                   | Requires gateway's WebSocket listener; CLI cannot send |
| iMessage | AppleScript / local RPC   | macOS login session               | Only works on macOS with logged-in user                |
| Telegram | Bot API (long polling)    | Bot token + numeric allowFrom IDs | Reliable from CLI and gateway                          |
| Slack    | Socket mode               | Bot token + app manifest          | Workspace-level auth                                   |

**Key properties:**

- All channels run simultaneously in the same gateway process
- Messages are routed to the AI agent with full conversation context
- `allowFrom` controls who can talk to the bot (per-channel authorization)
- Channels reconnect automatically after network interruptions
- The gateway handles message threading, typing indicators, read receipts where
  supported

**What this means for migration:** Any replacement must handle inbound message reception
from multiple platforms, route them to an AI, and send responses back — all without
human intervention.

---

## Scheduled Automation (Cron Runner)

OpenClaw includes a built-in cron scheduler that runs jobs on configurable schedules:

**Configuration:** `~/.openclaw/cron/jobs.json` — each job specifies:

- Cron expression (standard POSIX syntax)
- Model to use (with role-based aliases: `cheap`, `work`, `think`, `verify`)
- Prompt or workflow to execute
- Timeout (seconds)
- Provider routing preferences

**Operational features:**

- **Fallback chains** — if the primary model/provider fails, tries alternatives
  (Anthropic direct → OpenRouter → other providers)
- **Cooldown handling** — tracks provider rate limits, skips providers in cooldown
- **Consecutive error tracking** — counts failures per job, escalates after thresholds
- **Timeout management** — configurable per-job, kills long-running jobs gracefully
- **Silent success** — only notifies on failures or state changes, not routine success
- **Job health visibility** — `openclaw cron status` shows all jobs with last run time,
  error count, and model used

**Current job inventory (example instance):** 15 active jobs spanning health monitoring,
email triage, contact management, daily briefings, knowledge curation, and more —
running from every 15 minutes to weekly schedules.

**What this means for migration:** The cron runner is tightly integrated with the
gateway (shares auth profiles, provider state, memory). Jobs aren't just "run a prompt"
— they carry state between runs and benefit from the gateway's model routing.

---

## Memory System

OpenClaw uses a **three-tier memory architecture:**

### Tier 1: MEMORY.md (Always in Context)

- Curated essentials loaded into every conversation
- ~100 lines max, manually maintained
- Contains: key facts, active projects, important relationships, critical decisions

### Tier 2: Daily Observations

- `memory/YYYY-MM-DD.md` — raw observations captured throughout the day
- Today and yesterday auto-load into context
- Older days available via search

### Tier 3: Deep Knowledge

- Organized by type: `memory/people/`, `memory/projects/`, `memory/topics/`,
  `memory/decisions/`
- Vector-searchable via embeddings (LM Studio local or OpenAI fallback)
- The `librarian` skill promotes durable knowledge upward through tiers

**Persistence:** Memory lives in SQLite (`~/.openclaw/memory/main.sqlite`) for search,
with markdown files as the human-readable canonical source. Memory persists across all
sessions, conversations, and restarts.

**Embeddings:** Local embedding model (LM Studio, port 1234) generates vectors for
semantic search. Fleet machines connect to the master's LM Studio via Tailscale.

**What this means for migration:** Any replacement needs both structured storage (files)
and semantic search (embeddings). Claude Code has CLAUDE.md and auto-memory but no
vector search.

---

## Autonomous Workflows

Workflows are long-running autonomous agents that maintain state and learn over time.
Each workflow has:

- **AGENT.md** — the algorithm definition (upstream-owned, updated via this repo)
- **State files** — `agent_notes.md` (learned patterns), `rules.md` (user preferences),
  `logs/` (execution history) — all user-owned, never overwritten
- **Schedule** — cron expression for when to run
- **Model selection** — which model to use (cost/capability tradeoff)

### Workflow Inventory

| Workflow          | What It Does                                                                | Schedule               |
| ----------------- | --------------------------------------------------------------------------- | ---------------------- |
| email-steward     | Inbox triage — archive noise, surface important mail                        | Every 30 min, 7am-10pm |
| task-steward      | Classify work, create tasks, execute via sub-agents, QA results             | Every 30 min           |
| calendar-steward  | Daily briefing with travel logistics and meeting prep                       | 8 AM daily             |
| contact-steward   | Detect unknown contacts across WhatsApp/iMessage/Quo, classify and organize | 7 AM, 5 PM daily       |
| cron-healthcheck  | Detect broken cron jobs, auto-remediate common issues                       | Hourly at :05          |
| learning-loop     | Capture corrections → detect patterns → validate → promote to memory        | 11:30 PM daily         |
| llm-usage-report  | Daily LLM spend breakdown by session and model                              | 5 PM daily             |
| daily-report      | Previous day's cost summary                                                 | 5 PM daily             |
| security-sentinel | Research AI security threats, map to OpenClaw, verify fleet exposure        | Monday 4 AM weekly     |
| mailroom-steward  | Advanced email routing (not yet implemented)                                | —                      |

**Key workflow properties:**

- Workflows accumulate knowledge via `agent_notes.md` — they get smarter over time
- User preferences in `rules.md` customize behavior without touching the algorithm
- Execution logs provide audit trail and debugging
- Workflows can escalate to the human when confidence is low
- Prompt injection defenses built into sensitive workflows (email, contacts)

**What this means for migration:** Workflows depend on the gateway's cron runner, memory
system, and channel access. The learning/state accumulation is the hardest part to
replicate — it requires persistent storage that survives across runs.

---

## Skills Framework

Skills are standalone tools the AI agent can invoke:

- **Self-contained** — each skill is a standalone UV script (Python) or bash wrapper
  with inline dependencies (`# /// script` metadata)
- **No shared code** — zero coupling between skills
- **SKILL.md** — metadata file describing the skill, version, usage
- **Deployment** — copied to `~/.openclaw/workspace/skills/` on install/update

### Skill Categories

**Communication:** agentmail (email for AI), quo (business phone), tgcli (Telegram CLI),
vapi-calls (outbound voice calls)

**Knowledge:** parallel (web search), limitless (lifelog recall), fireflies (meeting
transcripts), fathom (meeting recordings), librarian (knowledge curation)

**Productivity:** asana (task management), todoist (task management), followupboss (CRM)

**Meta:** openclaw (self-management), gateway-restart (graceful restart),
smart-delegation (model routing), workflow-builder (design workflows),
create-great-prompts (prompt engineering guide)

**What this means for migration:** Skills are mostly API wrappers — they'd work in any
environment that can run Python scripts. The skill framework itself is trivially
portable. What matters is whether the calling environment (gateway vs Claude Code) can
invoke them.

---

## Identity and Personality

OpenClaw maintains persistent identity across all interactions:

| Template     | Purpose                                                |
| ------------ | ------------------------------------------------------ |
| AGENTS.md    | Workspace definition — how the AI should think and act |
| SOUL.md      | Personality — essence, name, communication style       |
| USER.md      | User profile — who the human is, preferences, context  |
| BOOT.md      | Startup routine — conversation recovery, pre-checks    |
| HEARTBEAT.md | Periodic checks — inbox, tasks, health (rotated daily) |
| TOOLS.md     | Machine-specific environment config                    |
| IDENTITY.md  | Quick reference card (one-page summary)                |

These templates are deployed to `~/.openclaw/workspace/` and loaded into every
conversation. They create a consistent persona that persists across sessions, channels,
and restarts.

**What this means for migration:** Claude Code's CLAUDE.md hierarchy (global → project →
local) serves a similar purpose. The identity templates could be adapted to CLAUDE.md
files. The main gap is that CLAUDE.md is project-scoped, while OpenClaw's identity is
global across all interactions.

---

## Fleet Management

OpenClaw supports multi-machine deployments managed from a central "fleet master":

- **Fleet state:** `~/openclaw-fleet/*.md` — one markdown file per remote server with
  connection details, current state, gaps, and update history
- **Push model:** Master machine is the source of truth; updates are pushed via SSH
- **Fleet command:** `/fleet` in Claude Code — assess, update, notify across machines
- **Graceful restarts:** `gateway-restart` skill ensures zero message loss during
  updates
- **Health monitoring:** Each machine runs its own health check cron; master can SSH in
  for deeper diagnosis
- **Security audits:** `security-sentinel` workflow SSHs into fleet machines for
  exposure mapping
- **Notification routing:** Two-lane model (admin alerts vs user notifications) with
  per-machine configuration

**What this means for migration:** Fleet management is entirely SSH-based and lives in
this repo (commands, skills, devops specs). It doesn't depend on the OpenClaw gateway
itself — it could be operated from Claude Code or any SSH-capable environment. The
gateway is what gets _managed_, not what does the managing.

---

## Model Routing

OpenClaw routes LLM requests through a sophisticated provider system:

**Role-based aliases:**

- `cheap` / `simple` — fast, inexpensive tasks (Haiku-class)
- `work` / `chat` — standard quality (Sonnet-class)
- `think` / `verify` — deep reasoning (Opus-class)

**Provider routing:**

- Anthropic direct API (primary)
- OpenRouter (fallback, access to non-Anthropic models)
- Per-job and per-workflow model specification
- Automatic fallback when primary provider fails or rate-limits

**Cooldown management:** Tracks rate limit state per provider, automatically routes
around providers in cooldown.

**What this means for migration:** Claude Code uses a single model per session (the one
you're subscribed to). There's no fallback chain, no provider routing, no cost-tier
selection. This is a significant capability difference for cost optimization.

---

## Health and Observability

**Health check cron:** Runs every 30 minutes, checking:

- Gateway liveness
- Model catalog (missing models)
- Cron job health (consecutive errors, timeouts)
- Disk and memory usage
- Log health (rotation, size)

**Auto-remediation:** Common issues are fixed automatically (restart hung gateway, clean
old logs, clear stuck jobs). Failures escalate to admin via Telegram.

**Logging:** Gateway logs rotate daily (`/tmp/openclaw/openclaw-YYYY-MM-DD.log`), with
error-only logs at `~/.openclaw/logs/gateway.err.log`.

**Dashboard:** Web UI at `http://127.0.0.1:18789/` for real-time monitoring.

**What this means for migration:** Claude Code has no equivalent observability layer.
There's no health monitoring, no auto-remediation, no dashboard. You'd be flying blind
unless you build monitoring externally.

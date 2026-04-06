# OpenClaw Model Configs, OpenRouter, and Jobs

How OpenClaw handles model selection, provider routing, and scheduled autonomous jobs.

## The Model Tier System

OpenClaw uses four model tiers. Each tier is an **alias** — a short name that resolves
to a specific model ID in the catalog. Aliases stay stable across provider changes and
model upgrades.

### Tiers

| Tier       | Model         | What it's for                                                                                                                                      |
| ---------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **haiku**  | Claude Haiku  | Fast, cheap. Checking known patterns, triage, high-frequency polling. The workhorse for anything that runs every 5-30 minutes.                     |
| **sonnet** | Claude Sonnet | Judgment calls. Triage that needs reasoning, daily reports, routing decisions. The sweet spot for "needs to think but doesn't need to think hard." |
| **opus**   | Claude Opus   | Deep synthesis and strategy. Daily reflections, security analysis, weekly reviews. The expensive one — used when quality matters more than speed.  |
| **grok**   | Grok 3        | Unfiltered perspectives. Zero guardrails, politically incorrect takes, dark humor. Falls back through OpenRouter if native unavailable.            |

Additional tiers on some instances:

| Tier               | Model                         | What it's for                                                                 |
| ------------------ | ----------------------------- | ----------------------------------------------------------------------------- |
| **llama-maverick** | Llama (via LM Studio)         | Local-only, offline tasks. Sleep routines, wind-down — runs without internet. |
| **default**        | Whatever the primary model is | Used when the job doesn't need a specific tier.                               |

### Smart Delegation (Real-Time Model Routing)

For live conversation, OpenClaw routes to one of three modes:

| Mode           | Model | Thinking       | When                                                             |
| -------------- | ----- | -------------- | ---------------------------------------------------------------- |
| **Direct**     | Opus  | off            | Default for everything — conversation, quick answers, daily life |
| **Deep Think** | Opus  | medium or high | Complex strategy, multi-factor decisions, hard reasoning         |
| **Unfiltered** | Grok  | default        | Politically incorrect, edgy, when guardrails are unwanted        |

Most messages stay in Direct mode. Escalation to Deep Think only happens when the
quality gain justifies 30-90 seconds of silence (no streaming during sub-agent work).

Reasoning levels for Deep Think:

- **low** — quick sanity check ("Is this contract clause standard?")
- **medium** — most escalations, analysis with tradeoffs ("Which job offer?")
- **high** — explicit "ultrathink" or genuinely high stakes ("Should I sell the
  company?")

## Provider Format (Where People Get Burned)

The same model has different IDs depending on which provider serves it. This is the #1
source of configuration errors.

| Provider             | Format                              | Example                                  |
| -------------------- | ----------------------------------- | ---------------------------------------- |
| **Anthropic direct** | `anthropic/claude-{tier}-{version}` | `anthropic/claude-sonnet-4-6`            |
| **OpenRouter**       | `openrouter/{org}/{model}`          | `openrouter/anthropic/claude-sonnet-4.6` |
| **xAI direct**       | `x-ai/{model}`                      | `x-ai/grok-3`                            |
| **OpenRouter xAI**   | `openrouter/{org}/{model}`          | `openrouter/x-ai/grok-3`                 |
| **LM Studio**        | `lmstudio/{org}/{model}`            | `lmstudio/meta/llama-maverick`           |

The critical difference: Anthropic direct uses **hyphens** in versions (`4-6`), while
OpenRouter uses **dots** (`4.6`). Getting this wrong causes silent failures.

### Fallback Chains

When a provider is down, OpenClaw falls through alternatives:

**Primary conversation:**

```
anthropic/claude-opus-4-6 → openrouter/openai/gpt-5.2 → anthropic/claude-sonnet-4-6
```

**Grok (unfiltered mode):**

```
x-ai/grok-3 → openrouter/x-ai/grok-3 → openrouter/openai/gpt-5.2 → handle directly
```

## Config Structure

Models are configured in `~/.openclaw/openclaw.json` under `agents.defaults`:

```
model.primary      → The main conversational model (e.g., anthropic/claude-opus-4-6)
model.fallbacks    → Ordered fallback chain when primary is unavailable
models             → Model catalog: maps model ID → {alias, params}
heartbeat.model    → Lightweight model for health pings (typically sonnet)
subagents.model    → Model for spawned sub-agents (typically sonnet)
```

Cron jobs can override the model per-job via `openclaw cron edit <id> --model <alias>`.

### The Discovery Rule

Model IDs are **never hardcoded from memory**. They're always verified against the live
catalog:

```bash
openclaw models list --all | grep -i sonnet
```

This exists because model names change constantly. A stale ID in a cron job fails
silently at 3am. The `update-model` skill enforces a mandatory 5-step verification
process: discover, validate, update, verify, monitor.

## Scheduled Jobs (Cron)

Jobs are the backbone of OpenClaw's autonomous behavior. Each runs on a cron schedule,
uses a specific model tier, and delivers results through a configured channel.

### Adding a Job

```bash
openclaw cron add \
  --name "my-job" \
  --cron "*/30 8-22 * * *" \
  --tz "<YOUR_TIMEZONE>" \
  --session isolated \
  --model sonnet \
  --announce
```

### Model Selection by Job Type

The principle: **cheap models for checking, expensive models for thinking.**

| Job Type                          | Tier           | Examples                                              |
| --------------------------------- | -------------- | ----------------------------------------------------- |
| High-frequency polling (5-30 min) | haiku          | Inbox triage, health checks, message stewards         |
| Daily reports and briefings       | sonnet         | Intelligence briefings, weekly reviews, update checks |
| Deep synthesis (daily/weekly)     | opus           | Nightly reflection, security sentinel                 |
| Unfiltered takes                  | grok           | EOD briefings with edgy commentary                    |
| Offline/local tasks               | llama-maverick | Sleep routines, wind-down                             |

### Delivery Modes

How job output reaches the user:

- **announce** — Posts to the configured channel after completion (daily briefings,
  reports)
- **in-prompt** — Silent on success, alerts only on failure or findings (health checks,
  inbox triage)
- **none** — Internal processing only, no user-facing output (reflection, memory
  maintenance)

### The Cron Fleet Manifest

All jobs are documented in a single source of truth: `devops/cron-fleet-manifest.md`. If
a job isn't listed there, it shouldn't be running. Each entry specifies the job name,
schedule, model tier, output topic, and delivery method.

## Workflows (Autonomous Agents)

Workflows are persistent agents triggered by cron jobs. Each maintains its own state and
learns over time:

```
workflows/<name>/
├── AGENT.md        # The algorithm (updated from config repo)
├── rules.md        # User preferences (never overwritten by updates)
├── agent_notes.md  # Patterns the agent has learned
└── logs/           # Execution history
```

The key design: `AGENT.md` updates when you update OpenClaw, but `rules.md` and
`agent_notes.md` belong to the running instance. Workflows genuinely improve over time
without losing learned behavior on update.

## Health Monitoring

The health check system runs every 30 minutes (haiku tier) and monitors gateway
liveness, model catalog health, cron job status, channel connectivity, and system
resources.

It follows a **silent success model** — zero output when healthy, alerts only on
failure. The `cron-healthcheck` workflow monitors the health check itself.

## Key Principles

1. **Discovery over memory** — Always verify model IDs against the live catalog
2. **Aliases over IDs** — User-facing config uses tier aliases, not full model IDs
3. **Cheap for checking, expensive for thinking** — Match tier to task complexity
4. **Silent success** — Jobs produce zero output when healthy
5. **Graceful degradation** — Fallback chains keep things running when a provider is
   down
6. **State in markdown** — All workflow state lives in files, not databases

# OpenClaw Model Configs, OpenRouter, and Jobs

A practical guide to how OpenClaw handles model configuration, provider routing, and
scheduled jobs.

## Model Configuration

Models are configured in `~/.openclaw/openclaw.json` across several scopes:

```
agents.defaults.model.primary      → Main conversational model
agents.defaults.model.fallbacks    → Ordered fallback chain
agents.defaults.models             → Model catalog (model ID → {alias, params})
agents.defaults.heartbeat.model    → Lightweight ping model
agents.defaults.subagents.model    → Model for spawned sub-agents
Per-cron payload.model             → Override per scheduled job
```

### Aliases vs. Full IDs

OpenClaw uses **aliases** (`sonnet`, `opus`, `haiku`, `grok`) in user-facing configs
like cron definitions, and **full model IDs** (`anthropic/claude-sonnet-4-6`) in the
actual catalog. Aliases are short, forwards-compatible, and resolve to whatever full ID
the catalog maps them to.

### Changing a Model

The `update-model` skill walks through a mandatory 5-step process:

1. **Discovery** — `openclaw models list --all` to see what's available (never guess)
2. **Validate** — Confirm the model ID exists in the catalog
3. **Update** — Change the config value
4. **Verify** — Run a test prompt to confirm the model responds
5. **Monitor** — Watch for failures in the first few hours

This exists because model names go stale fast — providers rename, version, and deprecate
constantly. A wrong model ID in a cron job fails silently at 3am.

## OpenRouter Integration

OpenRouter is a multi-provider gateway that gives access to models from many providers
through a single API. OpenClaw treats it as a first-class provider.

### Format Matters

Provider format differences are a common source of bugs:

| Provider         | Format                              | Example                                         |
| ---------------- | ----------------------------------- | ----------------------------------------------- |
| Anthropic direct | `anthropic/claude-{tier}-{version}` | `anthropic/claude-sonnet-4-6` (hyphens)         |
| OpenRouter       | `openrouter/{org}/{model}`          | `openrouter/anthropic/claude-sonnet-4.6` (dots) |

Note the subtle difference: Anthropic direct uses **hyphens** in version numbers
(`4-6`), while OpenRouter uses **dots** (`4.6`). Getting this wrong causes silent
failures.

### When OpenRouter Gets Used

- **Fallback chains** — When the primary provider is down, OpenRouter provides
  alternative routing to the same or equivalent models
- **Cross-provider access** — Models like Grok or GPT that aren't available through the
  primary provider
- **Cost optimization** — Some models are cheaper through OpenRouter depending on usage
  patterns

Example fallback chain:

```
Primary:   anthropic/claude-opus-4-6          (direct)
Fallback:  openrouter/openai/gpt-5.2          (cross-provider via OpenRouter)
Fallback:  anthropic/claude-sonnet-4-6         (cheaper direct fallback)
```

## Smart Delegation (Model Routing)

OpenClaw routes prompts to different models based on the task:

| Mode           | Model               | When                                     |
| -------------- | ------------------- | ---------------------------------------- |
| **Direct**     | Opus (thinking off) | Default conversation                     |
| **Deep Think** | Opus (thinking on)  | Complex strategy, multi-factor decisions |
| **Unfiltered** | Grok                | Edge cases, unfiltered perspectives      |

Escalation signals (when to upgrade from Direct to Deep Think):

- "Think hard about this", multi-factor decisions, complex debugging
- **Not** triggered by: long messages, multiple simple questions, casual chat

Grok fallback chain when native unavailable:

```
x-ai/grok-3 → openrouter/x-ai/grok-3 → openrouter/openai/gpt-5.2 → handle directly
```

## Scheduled Jobs (Cron)

Jobs are the backbone of OpenClaw's autonomous behavior. Each job runs on a cron
schedule, uses a specific model, and delivers results through a configured channel.

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

The general principle: **cheap models for checking, expensive models for thinking.**

| Job Type                         | Model                    | Rationale                                |
| -------------------------------- | ------------------------ | ---------------------------------------- |
| High-frequency checks (5-15 min) | Haiku                    | Fast, cheap, checking known patterns     |
| Triage and routing (15-30 min)   | Sonnet                   | Needs judgment but not deep reasoning    |
| Daily reports and briefings      | Opus                     | Synthesis across multiple sources        |
| Weekly reviews                   | Opus + extended thinking | Deep analysis, strategic recommendations |

### Delivery Modes

- **announce** — Posts output to the configured channel (daily briefings, reports)
- **in-prompt** — Silent on success, alerts on failure (health checks, triage)
- **none** — Internal processing only (nightly reflection, learning loops)

### Example Job Schedule

| Job                  | Schedule            | Model  | Delivery  |
| -------------------- | ------------------- | ------ | --------- |
| morning-briefing     | 8am daily           | haiku  | announce  |
| daily-report         | 7am daily           | sonnet | announce  |
| inbox-triage         | every 30m, 7am-10pm | haiku  | in-prompt |
| health-check         | every 30m           | haiku  | in-prompt |
| cron-healthcheck     | :05 past hour       | haiku  | in-prompt |
| nightly-reflection   | 11pm daily          | opus   | none      |
| weekly-security-scan | Mon 4am             | opus   | none      |

### The Cron Fleet Manifest

All jobs are documented in a single source of truth: `devops/cron-fleet-manifest.md`.
This is the canonical registry — if a job isn't listed there, it shouldn't be running.

## Workflows (Autonomous Agents)

Workflows are persistent autonomous agents triggered by cron jobs. Each workflow
maintains its own state and learns over time:

```
workflows/<name>/
├── AGENT.md        # The algorithm (updated from config repo)
├── rules.md        # User preferences (never overwritten by updates)
├── agent_notes.md  # Patterns the agent has learned
└── logs/           # Execution history
```

Key workflows:

| Workflow          | Schedule      | Purpose                                 |
| ----------------- | ------------- | --------------------------------------- |
| email-steward     | every 30m     | Inbox triage and routing                |
| task-steward      | hourly        | Task management and follow-up           |
| calendar-steward  | 8am daily     | Daily schedule prep                     |
| contact-steward   | 7am daily     | Contact discovery                       |
| security-sentinel | Mon 4am       | Threat research                         |
| cron-healthcheck  | :05 past hour | Monitor other cron jobs                 |
| learning-loop     | 3am nightly   | Memory maintenance and self-improvement |

The key design principle: `AGENT.md` gets updated when you update OpenClaw, but
`rules.md` and `agent_notes.md` belong to the running instance and are never
overwritten. This lets workflows improve over time without losing learned behavior.

## Health Monitoring

The health check system runs every 30 minutes and monitors:

- Gateway liveness and API connectivity
- Model catalog health (can models actually respond?)
- Cron job status (are jobs running on schedule?)
- Channel connectivity (can messages be delivered?)
- System resources (disk, memory)
- Log health (error patterns, anomalies)

It follows a **silent success model** — zero output when healthy, alerts only on
failure. The cron-healthcheck workflow monitors the health check itself (quis custodiet
ipsos custodes).

## Key Principles

1. **Discovery over memory** — Always verify model IDs against the live catalog. Never
   hardcode from memory.
2. **Silent success** — Jobs produce zero output when healthy. Only alert on failure.
3. **Cheap for checking, expensive for thinking** — Match model cost to task complexity.
4. **Prose over config** — Instructions in markdown, not JSON. Agents read markdown
   natively.
5. **State in files** — All workflow state lives in markdown files, versioned in git.
6. **Graceful degradation** — Fallback chains ensure service continuity when a provider
   is down.

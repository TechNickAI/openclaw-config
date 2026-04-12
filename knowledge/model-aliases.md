# Model Alias Standard

Role-based aliases that abstract away provider-specific model IDs. Cron jobs, workflow
AGENT.md files, and skill prompts should reference aliases — never hardcoded model IDs.

## Alias Table

| Alias           | Model ID                                   | Purpose                            |
| --------------- | ------------------------------------------ | ---------------------------------- |
| `cheap`         | `openrouter/stepfun/step-3.5-flash`        | Shell scripts, trivial tasks       |
| `simple`        | `openrouter/minimax/minimax-m2.7`          | Sentinels, healthchecks, triage    |
| `work`          | `openrouter/xiaomi/mimo-v2-pro`            | Stewards, inbox, browser work      |
| `chat-fallback` | `openrouter/google/gemini-3.1-pro-preview` | Backup when default is down        |
| `think`         | `openrouter/anthropic/claude-opus-4.6`     | Deep reasoning, nightly reflection |
| `verify`        | `openrouter/x-ai/grok-4.20`                | Cross-check, web-grounded          |

## Default Model

The default model is not an alias — it's the primary model used for conversations and
any task that doesn't specify an alias. Set via `agents.defaults.model.primary`.

### Subscription machines (preferred)

Machines with a ChatGPT subscription ($200/mo) use GPT-5.4 via the codex provider. This
is effectively unlimited and has the highest EQ score (73.2) of any model tested.
Requires an `openai-codex` auth profile with OAuth mode.

- **Primary:** `openai-codex/gpt-5.4`
- **Fallback 1:** `chat-fallback` (openrouter/google/gemini-3.1-pro-preview)
- **Fallback 2:** `work` (openrouter/xiaomi/mimo-v2-pro)
- **Heartbeat:** `openrouter/anthropic/claude-haiku-4.5`

### OpenRouter-only machines

Machines without a subscription fall back to Sonnet as the default.

- **Primary:** `openrouter/anthropic/claude-sonnet-4.6`
- **Fallback 1:** `chat-fallback` (openrouter/google/gemini-3.1-pro-preview)
- **Fallback 2:** `work` (openrouter/xiaomi/mimo-v2-pro)
- **Heartbeat:** `openrouter/anthropic/claude-haiku-4.5`

## Cost Ladder

```
cheap ($0.15) → simple ($0.53) → work ($1.50) → verify ($3.00) → chat-fallback ($4.50) → think ($10.00)
```

On subscription machines, the default model (GPT-5.4) is effectively free — only the
aliases above incur per-token cost.

## EQ Benchmarks (EQ-Bench v3, 0-100)

| Alias           | EQ Score | Notable Traits                              |
| --------------- | -------- | ------------------------------------------- |
| `default`       | 73.2     | Highest EQ, best insight (15.8) — GPT-5.4   |
| `cheap`         | 69.25    | Best EQ-per-dollar in the field             |
| `simple`        | 68.75    | Best theory of mind (15.1), subtext (16.3)  |
| `work`          | 70.55    | Highest humanlike (15.1), analytical (18.1) |
| `chat-fallback` | 68.95    | Balanced, fast (127 tok/s)                  |
| `think`         | 71.85    | Highest empathy (14.9), warmth (13.6)       |
| `verify`        | 68.55    | Web-grounded, fastest model (271 tok/s)     |

Source: https://heartcentered.ai/model-benchmarks/

## Design Principles

- **No direct `anthropic/*` calls** — always via `openrouter/anthropic/*`
- **Alias, not model ID** — cron jobs use alias names so the underlying model can be
  swapped fleet-wide in one config edit
- **Every alias = unique model** — distinct line items in OpenRouter dashboard for spend
  visibility by job type
- **`cheap` → `simple` → `work` → `think`** = quality/cost spectrum. Name reflects the
  job's needs, not the model's brand.
- **Default is not an alias** — it's the primary model set in config. Subscription
  machines use GPT-5.4 (unlimited); others use Sonnet.
- **`verify`** = always a different model family for genuine cross-validation
- **Heart-centered selection** — models chosen for emotional intelligence alongside
  capability, not just IQ and cost. EQ-Bench v3 scores inform every alias choice.

## Applying to a New Machine

### Aliases (all machines)

```bash
openclaw models aliases add cheap openrouter/stepfun/step-3.5-flash
openclaw models aliases add simple openrouter/minimax/minimax-m2.7
openclaw models aliases add work openrouter/xiaomi/mimo-v2-pro
openclaw models aliases add chat-fallback openrouter/google/gemini-3.1-pro-preview
openclaw models aliases add think openrouter/anthropic/claude-opus-4.6
openclaw models aliases add verify openrouter/x-ai/grok-4.20
```

### Default model — Subscription (preferred)

```bash
openclaw auth add openai-codex --mode oauth
openclaw config set agents.defaults.model.primary "openai-codex/gpt-5.4"
openclaw config set agents.defaults.model.fallbacks '["openrouter/google/gemini-3.1-pro-preview", "openrouter/xiaomi/mimo-v2-pro"]'
openclaw config set agents.defaults.heartbeat.model "openrouter/anthropic/claude-haiku-4.5"
```

### Default model — OpenRouter only

```bash
openclaw config set agents.defaults.model.primary "openrouter/anthropic/claude-sonnet-4.6"
openclaw config set agents.defaults.model.fallbacks '["openrouter/google/gemini-3.1-pro-preview", "openrouter/xiaomi/mimo-v2-pro"]'
openclaw config set agents.defaults.heartbeat.model "openrouter/anthropic/claude-haiku-4.5"
```

## History

- **2026-04-10:** Removed `chat` alias — default model is not an alias, it's config.
  Subscription machines use GPT-5.4 as default (unlimited via ChatGPT subscription).
  OpenRouter-only machines fall back to Sonnet.
- **2026-04-08:** Reverted chat/default primary back to Sonnet — Haiku quality was
  noticeably worse in practice. Heartbeat stays Haiku (cost-appropriate for pings).
- **2026-04-07:** Heart-centered model selection overhaul. Replaced Sonnet with Haiku
  for chat (67% savings, vision support, same agentic score). Added EQ-Bench v3 scoring
  as selection criteria. Introduced subscription overlay (codex/GPT-5.4). New value
  models: Step 3.5 Flash (cheap), MiniMax M2.7 (simple), MiMo-V2-Pro (work). Grok
  replaces Qwen for verify (web-grounded fact-checking).
- **2026-04-04:** Migrated from direct Anthropic API to OpenRouter after Anthropic cut
  off third-party tool access to Claude subscriptions. Old aliases (`haiku`, `sonnet`,
  `opus`) replaced with role-based names.

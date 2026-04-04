# Model Alias Standard

Role-based aliases that abstract away provider-specific model IDs. Cron jobs, workflow
AGENT.md files, and skill prompts should reference aliases — never hardcoded model IDs.

## Alias Table

| Alias           | Model ID                                   | Purpose                             |
| --------------- | ------------------------------------------ | ----------------------------------- |
| `cheap`         | `openrouter/free`                          | Shell scripts, trivial tasks        |
| `simple`        | `openrouter/anthropic/claude-haiku-4.5`    | Sentinels, healthchecks, triage     |
| `work`          | `openrouter/openai/gpt-5.4`                | Stewards, inbox, browser work       |
| `chat`          | `openrouter/anthropic/claude-sonnet-4.6`   | Main session (agent's voice)        |
| `chat-fallback` | `openrouter/google/gemini-3.1-pro-preview` | Chat backup                         |
| `think`         | `openrouter/anthropic/claude-opus-4.6`     | Deep reasoning, nightly reflection  |
| `verify`        | `openrouter/qwen/qwen3.6-plus:free`        | Cross-check, different model family |
| `grok`          | `openrouter/x-ai/grok-4.1-fast`            | Web-grounded queries                |
| `local`         | `lmstudio/google/gemma-3-4b`               | Local inference                     |

## Default Model Chain

- **Primary:** `chat` (openrouter/anthropic/claude-sonnet-4.6)
- **Fallback 1:** `chat-fallback` (openrouter/google/gemini-3.1-pro-preview)
- **Fallback 2:** `work` (openrouter/openai/gpt-5.4)
- **Heartbeat:** `simple` (openrouter/anthropic/claude-haiku-4.5)

## Design Principles

- **No direct `anthropic/*` calls** — always via `openrouter/anthropic/*`
- **Alias, not model ID** — cron jobs use alias names so the underlying model can be
  swapped fleet-wide in one config edit
- **Different families for spend visibility** — Anthropic spend = conversations, OpenAI
  = automation, Google = fallback. Easy to split on OpenRouter dashboard.
- **`cheap` → `simple` → `work` → `chat` → `think`** = quality/cost spectrum. Name
  reflects the job's needs, not the model's brand.
- **`verify`** = always a different model family for genuine cross-validation

## Applying to a New Machine

Set in `openclaw.json` under `agents.defaults.models`, or use the CLI:

```bash
openclaw models aliases add cheap openrouter/free
openclaw models aliases add simple openrouter/anthropic/claude-haiku-4.5
openclaw models aliases add work openrouter/openai/gpt-5.4
openclaw models aliases add chat openrouter/anthropic/claude-sonnet-4.6
openclaw models aliases add chat-fallback openrouter/google/gemini-3.1-pro-preview
openclaw models aliases add think openrouter/anthropic/claude-opus-4.6
openclaw models aliases add verify openrouter/qwen/qwen3.6-plus:free
```

## History

- **2026-04-04:** Migrated from direct Anthropic API to OpenRouter after Anthropic cut
  off third-party tool access to Claude subscriptions. Old aliases (`haiku`, `sonnet`,
  `opus`) replaced with role-based names.

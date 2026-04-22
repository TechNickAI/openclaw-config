# 9Router Full Setup Guide

Complete setup for 9Router + OpenClaw on a fresh machine: install the router,
authenticate providers, run it as a daemon, wire it into OpenClaw with both
OpenAI-compat and Anthropic-native providers, and verify.

**What 9Router is:** A local smart-router daemon that exposes an OpenAI-compatible API
(and Anthropic Messages API) at `http://127.0.0.1:20128`. It aggregates your paid
subscriptions, OAuth accounts, and free/cheap providers behind a single endpoint with
automatic fallback and quota tracking.

**Why we use it:** One endpoint for all models, OAuth-backed Claude Code / Codex /
Gemini CLI access without API keys, quota maximization, and seamless fallback across
providers.

---

## Architecture

```
OpenClaw (or any CLI tool)
    │
    │  http://127.0.0.1:20128/v1            ← OpenAI-compat endpoint
    │  http://127.0.0.1:20128/v1/messages   ← Anthropic Messages endpoint
    ↓
9Router daemon (Node.js, port 20128)
    │
    ├─→ Claude OAuth (via Claude Code / Antigravity login)
    ├─→ Codex OAuth
    ├─→ Gemini CLI OAuth
    ├─→ OpenRouter (API key)
    ├─→ Direct provider API keys (Anthropic, OpenAI, xAI, etc.)
    └─→ Free tiers (iFlow, Qwen, Kiro, etc.)
```

Data lives under `~/.local/share/9router/` (dashboard state, OAuth tokens, usage logs,
request history). The dashboard UI is at `http://localhost:20128/dashboard`.

---

## Install

### Option A — npm global (recommended for most setups)

```bash
npm install -g 9router
9router
```

This launches the daemon and opens the dashboard at `http://localhost:20128/dashboard`.

### Option B — From source

Clone into `~/src/9router`:

```bash
cd ~/src
git clone https://github.com/decolua/9router.git
cd 9router
cp .env.example .env
npm install
npm run build    # builds .next/standalone/server.js
```

Source mode is worth it if you want to pin a specific version or read the code while
configuring.

---

## Run as a daemon (macOS LaunchAgent)

Running `9router` in a terminal works for setup but you want it auto-starting on login
and surviving reboots. Install a LaunchAgent.

Create `~/Library/LaunchAgents/com.<USER>.9router.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "https://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.<USER>.9router</string>

  <key>ProgramArguments</key>
  <array>
    <!-- Adjust node path to match your installation -->
    <string>/Users/<USER>/.nvm/versions/node/v24.13.0/bin/node</string>
    <string>/Users/<USER>/src/9router/.next/standalone/server.js</string>
  </array>

  <key>WorkingDirectory</key>
  <string>/Users/<USER>/src/9router</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>JWT_SECRET</key>
    <string>CHANGE_ME_RANDOM_SECRET</string>
    <key>INITIAL_PASSWORD</key>
    <string>CHANGE_ME_DASHBOARD_PASSWORD</string>
    <key>PORT</key>
    <string>20128</string>
    <key>HOSTNAME</key>
    <string>127.0.0.1</string>
    <key>BASE_URL</key>
    <string>http://127.0.0.1:20128</string>
    <key>NEXT_PUBLIC_BASE_URL</key>
    <string>http://127.0.0.1:20128</string>
    <key>DATA_DIR</key>
    <string>/Users/<USER>/.local/share/9router</string>
    <key>NODE_ENV</key>
    <string>production</string>
  </dict>

  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>

  <key>StandardOutPath</key>
  <string>/Users/<USER>/.local/share/9router/launchd.out.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/<USER>/.local/share/9router/launchd.err.log</string>
</dict>
</plist>
```

Notes:

- **Bind to `127.0.0.1` only.** This daemon holds OAuth tokens and API keys. Never
  expose it on `0.0.0.0` unless you know what you're doing.
- `JWT_SECRET` — generate with `openssl rand -base64 32`.
- `INITIAL_PASSWORD` — the dashboard login password. Change it after first use.
- Npm-global install users: replace the `ProgramArguments` with the path to the
  installed `9router` binary (`which 9router` to find it).

Load and start:

```bash
launchctl load ~/Library/LaunchAgents/com.<USER>.9router.plist
launchctl list | grep 9router   # verify it's running
```

Health check:

```bash
curl -s http://127.0.0.1:20128/v1/models -H "Authorization: Bearer <your-api-key>" | head
```

Logs:

```bash
tail -f ~/.local/share/9router/launchd.out.log
tail -f ~/.local/share/9router/launchd.err.log
```

---

## Connect providers

Open `http://localhost:20128/dashboard` and sign in with your `INITIAL_PASSWORD`.

### Recommended connections (in priority order)

1. **Claude** (OAuth via Claude Code login) — primary, uses your Claude Code
   subscription quota
2. **Codex** (OAuth) — GPT-5.x via ChatGPT subscription
3. **Gemini CLI** (OAuth) — Gemini Pro via Google subscription
4. **OpenRouter** (API key) — fallback for anything not covered above, plus exotic
   models
5. **Direct provider keys** — only if you already pay for them (Anthropic, OpenAI, xAI)

### Generate an API key

In Dashboard → **API Keys** → create a new key. This is the key OpenClaw will use. Save
it somewhere safe — you'll paste it into `openclaw.json`.

### Model naming convention inside 9Router

| Prefix           | Source                                                                                                |
| ---------------- | ----------------------------------------------------------------------------------------------------- |
| `cc/`            | Claude Code OAuth (e.g. `cc/claude-opus-4-7`, `cc/claude-sonnet-4-6`, `cc/claude-haiku-4-5-20251001`) |
| `cx/`            | Codex OAuth (e.g. `cx/gpt-5.4`, `cx/gpt-5.4-mini`)                                                    |
| `gm/`            | Gemini CLI OAuth                                                                                      |
| `openrouter/...` | OpenRouter (full OpenRouter model ID preserved)                                                       |

List available models:

```bash
curl -s http://127.0.0.1:20128/v1/models \
  -H "Authorization: Bearer <api-key>" \
  | python3 -m json.tool | head -40
```

---

## Wire into OpenClaw

The critical insight: **9Router serves two different APIs on the same port**, and
OpenClaw talks to them through different provider entries.

| 9Router endpoint                                        | OpenClaw `api` field | Best for                                                  |
| ------------------------------------------------------- | -------------------- | --------------------------------------------------------- |
| `http://127.0.0.1:20128/v1` (OpenAI-compat)             | `openai-completions` | GPT models, OpenRouter-routed models, anything non-Claude |
| `http://127.0.0.1:20128/v1/messages` (Anthropic-native) | `anthropic-messages` | Claude models — preserves structured thinking blocks      |

**Route Claude through `anthropic-messages`. Everything else goes through
`openai-completions`.**

If you route Claude through the OpenAI-compat path, reasoning can leak into visible
reply text as `<thinking>…</thinking>` tags because the bridge translates Anthropic's
structured thinking blocks into a different shape that OpenClaw's renderer doesn't
always catch cleanly.

### How OpenClaw detects reasoning

Two mechanisms, in order of reliability:

1. **Structured Anthropic blocks** — the provider returns
   `content_block.type: "thinking"` and `content_block.type: "text"` as separate blocks.
   OpenClaw handles them as distinct reasoning events and keeps thinking out of
   user-visible text.
2. **Compat parsing for OpenAI-style streams** — OpenClaw looks for `reasoning_content`,
   `reasoning`, `reasoning_text`, or `reasoning_details` fields in delta chunks and
   converts them into internal reasoning blocks.

There's also a text sanitization layer that strips `<thinking>`, `<think>`, and
`<thought>` tags from visible assistant text, but this is a fallback — don't rely on it.
The native Anthropic path is the right solution.

### `/reasoning` command

Per-session visibility control:

| Command             | Effect                                                      |
| ------------------- | ----------------------------------------------------------- |
| `/reasoning on`     | Reasoning is visible in the UI when the channel supports it |
| `/reasoning off`    | Hide reasoning entirely                                     |
| `/reasoning stream` | Stream reasoning live (Telegram supports this)              |

Default is hidden unless enabled.

### Provider config (`~/.openclaw/openclaw.json`)

Add both providers under `models.providers`:

```json
"9router": {
  "baseUrl": "http://127.0.0.1:20128/v1",
  "apiKey": "<9router-api-key>",
  "api": "openai-completions",
  "injectNumCtxForOpenAICompat": false,
  "models": [
    {
      "id": "cx/gpt-5.4",
      "name": "GPT-5.4 via 9Router",
      "api": "openai-completions",
      "reasoning": true,
      "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 200000,
      "maxTokens": 32000
    }
  ]
},
"9router-anthropic": {
  "baseUrl": "http://127.0.0.1:20128",
  "apiKey": "<9router-api-key>",
  "api": "anthropic-messages",
  "models": [
    {
      "id": "cc/claude-opus-4-7",
      "name": "Claude Opus 4.7 via 9Router (Anthropic)",
      "api": "anthropic-messages",
      "reasoning": true,
      "input": ["text", "image"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 200000,
      "maxTokens": 32000
    },
    {
      "id": "cc/claude-sonnet-4-6",
      "name": "Claude Sonnet 4.6 via 9Router (Anthropic)",
      "api": "anthropic-messages",
      "reasoning": true,
      "input": ["text", "image"],
      "contextWindow": 200000,
      "maxTokens": 32000
    },
    {
      "id": "cc/claude-haiku-4-5-20251001",
      "name": "Claude Haiku 4.5 via 9Router (Anthropic)",
      "api": "anthropic-messages",
      "reasoning": true,
      "input": ["text", "image"],
      "contextWindow": 200000,
      "maxTokens": 16000
    }
  ]
}
```

**baseUrl detail:** for `anthropic-messages`, use the server root (no trailing `/v1`).
OpenClaw normalizes this and appends `/v1/messages` internally.

### Aliases

Under `agents.defaults.models`, map friendly names to concrete provider/model IDs:

```json
"models": {
  "9router-anthropic/cc/claude-opus-4-7":         { "alias": "9router-opus" },
  "9router-anthropic/cc/claude-sonnet-4-6":       { "alias": "sonnet" },
  "9router-anthropic/cc/claude-haiku-4-5-20251001": { "alias": "haiku" },
  "9router/cx/gpt-5.4":                           { "alias": "work" },
  "9router/cx/gpt-5.4-mini":                      { "alias": "simple" }
}
```

### Primary and fallbacks

```json
"model": {
  "primary": "9router-anthropic/cc/claude-opus-4-7",
  "fallbacks": [
    "openai-codex/gpt-5.4",
    "openrouter/google/gemini-3.1-pro-preview"
  ]
}
```

### Apply and restart

```bash
# Restart the OpenClaw gateway to pick up the new providers
# (or use gateway config.patch / gateway restart from inside a session)
```

---

## Verification checklist

Run through all of these on a fresh setup:

**9Router daemon:**

- [ ] `launchctl list | grep 9router` shows it running
- [ ] `curl -s http://127.0.0.1:20128/v1/models -H "Authorization: Bearer <key>"`
      returns a model list
- [ ] Dashboard loads at `http://localhost:20128/dashboard`
- [ ] At least one provider connection shows `testStatus: active`

**Anthropic Messages endpoint:**

```bash
curl -sS http://127.0.0.1:20128/v1/messages \
  -H "x-api-key: <9router-key>" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"cc/claude-opus-4-7","max_tokens":64,"messages":[{"role":"user","content":"say hi"}]}'
```

Should return a structured response with `content: [{type: "text", ...}]`.

**OpenClaw integration:**

- [ ] `openclaw models list` shows both `9router/...` and `9router-anthropic/...`
      entries
- [ ] Gateway restart completes without errors
- [ ] A reasoning-heavy prompt returns a clean reply with no `<thinking>` leakage
- [ ] `/reasoning on` and `/reasoning off` both behave as expected
- [ ] Aliases resolve: `/model haiku` works

---

## Operational notes

**Token refresh:** 9Router auto-refreshes OAuth tokens. If a provider starts failing,
check the dashboard for the connection's error state — most common cause is an expired
refresh token that needs a one-click re-auth.

**Quota tracking:** The dashboard shows usage per provider so you can see when your
Claude Code subscription is near reset. Fallbacks kick in automatically.

**Data directory:** `~/.local/share/9router/` holds:

- `db.json` — all provider connections, OAuth tokens, API keys (back this up for
  same-machine disaster recovery; contains secrets; see migration notes below for
  cross-machine setup)
- `usage.json` — per-provider quota tracking
- `request-details.json` — recent request log for debugging
- `log.txt` — application log
- `launchd.{out,err}.log` — daemon stdout/stderr

**Migrating to a new machine:** Copy the LaunchAgent plist (updating paths for the new
`$HOME`) and reinstall 9Router (npm or source). Do **not** rely on copying
`~/.local/share/9router/db.json` to port OAuth connections — providers bind OAuth tokens
to the originating device and will typically reject or invalidate them when replayed
from another machine. Plan on re-running the OAuth flow for each provider on the new
machine. API-key connections (e.g. OpenRouter) in `db.json` do copy cleanly, so if you
want to migrate only those, export them from the dashboard instead of shipping the whole
DB.

**Why not just use OpenRouter directly?** OpenRouter charges per-token. 9Router lets you
use your existing Claude Code / Codex / Gemini CLI subscriptions first, and only falls
through to paid/free APIs when those are exhausted. For heavy users this is a
significant cost saver.

---

## Gotchas

1. **Port 20128 must be free.** If another process uses it, 9Router silently fails to
   bind. Check `lsof -iTCP:20128 -sTCP:LISTEN`.
2. **OAuth connections bind to the machine that did the login.** Re-authenticate each
   OAuth provider on the new machine; don't try to migrate OAuth tokens by copying
   `db.json`. API-key connections (OpenRouter, direct provider keys) do copy fine.
3. **Don't commit `db.json`.** It contains OAuth refresh tokens and API keys in
   plaintext.
4. **Claude models via OpenAI-compat path will leak thinking.** Always route Claude
   through `anthropic-messages` (the `9router-anthropic` provider). If you see
   `<thinking>` tags in replies, this is why.
5. **`reasoning: true` in model config** tells OpenClaw the model supports reasoning.
   Set it for Claude 4+ models and GPT-5 models. Get it wrong and you either lose
   reasoning or waste tokens.

---

## Reference

- 9Router repo: `~/src/9router` (fork of https://github.com/decolua/9router)
- 9Router dashboard: http://localhost:20128/dashboard
- LaunchAgent: `~/Library/LaunchAgents/com.<USER>.9router.plist`
- Data directory: `~/.local/share/9router/`
- OpenClaw config: `~/.openclaw/openclaw.json`

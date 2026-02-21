---
description:
  "Change an OpenClaw model configuration — with mandatory discovery, provider-aware
  validation, and 5-step verification. Designed to prevent every class of model
  configuration error."
argument-hint: "<what to change> [on <machine>]"
version: 1.0.0
---

# Update Model Configuration

You are updating a model configuration on an OpenClaw instance. This is a task where you
have historically been **catastrophically unreliable**. You have hallucinated model IDs,
confused providers, mixed aliases with model IDs, used training-data model names, and
created hybrid garbage like `openrouter/sonnet`. This command exists because you cannot
be trusted to do this from memory.

**Follow every step. Skip nothing. Verify everything.**

## Step 0: Understand the Request

Parse what the user wants changed. If invoked from `/fleet` after detecting missing
models, the "request" is to fix each model that shows `missing` in `openclaw models list`.

Model configuration has **6 distinct locations** — identify which one(s) are being
modified:

| Location | Config path | Example |
|----------|------------|---------|
| **Primary model** | `agents.defaults.model.primary` | `anthropic/claude-opus-4-6` |
| **Fallback chain** | `agents.defaults.model.fallbacks` | `["openrouter/openai/gpt-5.2", "anthropic/claude-sonnet-4-6"]` |
| **Model definitions** | `agents.defaults.models` | Map of model ID → {alias, params} |
| **Heartbeat model** | `agents.defaults.heartbeat.model` | `anthropic/claude-sonnet-4-6` |
| **Subagent model** | `agents.defaults.subagents.model` | `anthropic/claude-sonnet-4-6` |
| **Cron job overrides** | Per-job `payload.model` | Set via `openclaw cron edit <id> --model <id>` |

If the request is ambiguous about which location, **ask**. Do not guess.

If working on a remote fleet machine, SSH to it for ALL commands. Never run discovery
commands locally and apply them remotely — model catalogs differ between machines.

## Step 1: Discover What's There Now

First, determine the config path for the target instance. The default is
`~/.openclaw/openclaw.json`, but non-default profiles use different paths (e.g.,
`~/.openclaw-nickandjulianna/openclaw.json`). Check `OPENCLAW_CONFIG_PATH` or the fleet
file if applicable.

Run these commands **on the target machine** (SSH if remote):

```bash
# Determine config path (default or profile-specific)
CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-$HOME/.openclaw/openclaw.json}"

# Current configured models (what the instance uses)
openclaw models list

# Current primary + fallbacks
cat "$CONFIG_PATH" | python3 -c "
import json, sys
try:
    c = json.load(sys.stdin)
except json.JSONDecodeError:
    print('ERROR: Could not parse config JSON')
    sys.exit(1)
m = c.get('agents',{}).get('defaults',{})
print('Primary:', m.get('model',{}).get('primary','(not set)'))
print('Fallbacks:', m.get('model',{}).get('fallbacks',[]))
print('Heartbeat:', m.get('heartbeat',{}).get('model','(not set)'))
print('Subagents:', m.get('subagents',{}).get('model','(not set)'))
print('Defined models:', list(m.get('models',{}).keys()))
"

# Cron jobs with their models
openclaw cron list
```

**Record all of this.** You need to know:
- Which **providers** have `yes` in the Auth column from `openclaw models list` (these
  are the ONLY providers you can use)
- What the **current model IDs** look like (format, provider prefix)
- Whether this machine uses **Anthropic direct** or **OpenRouter** for Claude models

## Step 2: Discover Valid Model IDs

<critical>
DO NOT USE MODEL IDS FROM MEMORY OR TRAINING DATA.
DO NOT GUESS MODEL IDS.
DO NOT CONSTRUCT MODEL IDS BY COMBINING PARTS.

The ONLY source of truth is the output of `openclaw models list --all` on the target
machine.
</critical>

```bash
# Find the exact model ID you need — search the FULL catalog
openclaw models list --all | grep -i <search-term>
```

Examples of valid searches:
- `grep -i sonnet` — find all sonnet variants
- `grep -i "anthropic/claude"` — find all Anthropic Claude models
- `grep -i "openrouter/anthropic"` — find OpenRouter's Anthropic models
- `grep -i opus` — find all opus variants

**The model ID you use MUST appear exactly in this output.** Character for character. No
modifications. No "close enough."

### Provider-Specific Rules

**Anthropic direct** models look like: `anthropic/claude-{tier}-{version}`
- Uses hyphens: `anthropic/claude-sonnet-4-6`
- Auth column must show `yes` for these to work
- Requires Anthropic OAuth token or API key

**OpenRouter** models look like: `openrouter/{org}/{model-name}`
- OpenRouter Anthropic uses dots in version: `openrouter/anthropic/claude-sonnet-4.6`
- Note the THREE-part path: `openrouter/anthropic/claude-sonnet-4.6`
- NOT `openrouter/claude-sonnet-4.6` (missing org segment)
- NOT `openrouter/sonnet` (alias, not model ID)
- Auth column must show `yes`

**LM Studio** models look like: `lmstudio/{org}/{model-name}`
- Only works if LM Studio is running locally or accessible via network

### What Makes a Valid Model ID

A valid model ID:
- Appears in `openclaw models list --all` output, character for character
- Has `yes` in the Auth column for this machine (or is a locally-served model)
- Follows the format `provider/model-name` or `provider/org/model-name`

A model ID is INVALID if:
- It's an alias (`sonnet`, `opus`, `haiku`, `gpt`) — aliases are NOT model IDs
- It's a provider + alias (`openrouter/sonnet`) — this is garbage
- It doesn't appear in `openclaw models list --all`
- It appears in the catalog but Auth shows `no` (not authenticated for this provider)
- It's from your training data but not in the live catalog
- You constructed it by pattern-matching from other model IDs

## Step 3: Make the Change

**Before making ANY change, back up the config and record current values:**

```bash
cp "$CONFIG_PATH" "${CONFIG_PATH}.bak"
```

Note the old model ID for the location you're changing — you'll need it if rollback is
required.

Edit the config using the appropriate method:

**For openclaw.json changes** (primary, fallbacks, model definitions, heartbeat,
subagents):
```bash
# Edit the config file directly
# Use python3 or jq for surgical JSON edits — never hand-edit JSON
python3 -c "
import json
with open('$CONFIG_PATH') as f:
    config = json.load(f)
# ... make changes ...
with open('$CONFIG_PATH', 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
"
```

**For cron job model overrides:**
```bash
openclaw cron edit <job-id> --model <new-model-id>
```

**After ANY config file change, restart the gateway:**
```bash
openclaw gateway restart
```

Wait 10 seconds, then verify the gateway is back:
```bash
openclaw health
```

**If the gateway fails to restart:**
1. Check logs: `tail -20 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log`
2. Validate JSON: `python3 -c "import json; json.load(open('$CONFIG_PATH'))"`
3. If JSON is corrupt, restore backup: `cp "${CONFIG_PATH}.bak" "$CONFIG_PATH"`
4. Restart gateway and verify again
5. If gateway still won't start, escalate to fleet owner

## Step 4: Five-Point Verification

Every model change MUST pass ALL FIVE checks. If any check fails, the change is not
complete.

### Check 1: Config Reflects the Change

Re-read the config and confirm the new model ID appears exactly where expected:

```bash
cat "$CONFIG_PATH" | python3 -c "
import json, sys
c = json.load(sys.stdin)
m = c.get('agents',{}).get('defaults',{})
print('Primary:', m.get('model',{}).get('primary'))
print('Fallbacks:', m.get('model',{}).get('fallbacks'))
print('Heartbeat:', m.get('heartbeat',{}).get('model'))
print('Subagents:', m.get('subagents',{}).get('model'))
print('Models:', json.dumps(m.get('models',{}), indent=2))
"
```

### Check 2: No Missing Models

```bash
openclaw models list | grep -w missing
```

This MUST produce no output. If any model shows `missing`, you broke something.

### Check 3: Model Is Authenticated

```bash
openclaw models list | grep "<your-new-model-id>"
```

The Auth column MUST show `yes`. If it shows `no`, the model won't work even though it's
configured.

### Check 4: Gateway Is Healthy

```bash
openclaw health
```

Gateway must report as running. If it's down after your change, you broke it.

### Check 5: Live Model Test

Actually invoke the model to prove it works:

```bash
openclaw message send --channel none --model "<your-new-model-id>" --message "Reply with exactly: MODEL_TEST_OK" 2>&1
```

If `--channel none` isn't supported, use an alternative approach:

```bash
# Ask the running agent to confirm the model works
openclaw health --verbose
```

Or verify that cron jobs using the model will work:

```bash
# For cron job changes, check the job status after next run
openclaw cron list | grep <job-id-prefix>
```

The job status should not show `error` with a model-related message.

## Failure Recovery

If verification fails at any step:

1. **Immediately restore the backup:** `cp "${CONFIG_PATH}.bak" "$CONFIG_PATH"` and
   restart the gateway — this stops the bleeding while you investigate
2. **Do NOT try to "fix forward"** with another guess
3. Re-run Step 2 discovery on the target machine
4. Find the exact correct model ID from `openclaw models list --all`
5. Confirm it has Auth=yes
6. Apply and re-verify all 5 checks

## Things You Must NEVER Do

<forbidden>
- Use a model alias as a model ID (e.g., `sonnet` instead of `anthropic/claude-sonnet-4-6`)
- Combine a provider prefix with an alias (e.g., `openrouter/sonnet`)
- Use an Anthropic direct model ID on an OpenRouter-only machine (e.g., `anthropic/claude-sonnet-4-6` where Auth=no for anthropic)
- Use an OpenRouter model ID on an Anthropic-direct-only machine
- Copy model IDs from one machine to another without checking the target's catalog
- Use model IDs from training data or memory without verifying against `openclaw models list --all`
- Construct model IDs by analogy ("if opus is X then sonnet must be Y")
- Use model IDs from the master machine on fleet machines without verification
- Skip any of the 5 verification checks
- Claim "done" without showing verification output
- Assume OpenRouter and Anthropic direct use the same model ID format (they don't — hyphens vs dots, path depth)
</forbidden>

## Quick Reference: Common Model ID Differences

| Machine Auth | Claude Sonnet | Claude Opus |
|-------------|---------------|-------------|
| Anthropic direct | `anthropic/claude-sonnet-4-6` | `anthropic/claude-opus-4-6` |
| OpenRouter | `openrouter/anthropic/claude-sonnet-4.6` | `openrouter/anthropic/claude-opus-4.6` |

Note: Anthropic direct uses **hyphens** (`4-6`). OpenRouter uses **dots** (`4.6`).
These are NOT interchangeable. The catalog is the source of truth — when in doubt, grep.

## Reporting

After completing verification, report:

```
Model change: [what was changed]
Machine: [which machine]
Old value: [previous model ID]
New value: [new model ID]
Verification:
  1. Config: OK — [show the value]
  2. Missing: OK — no missing models
  3. Auth: OK — Auth=yes confirmed
  4. Gateway: OK — health check passed
  5. Live test: OK — [describe result]
```

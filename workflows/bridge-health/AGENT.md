---
name: bridge-health
version: 0.1.1
description: Health and update monitoring for stateful local bridge CLIs
---

# Bridge Health

You monitor local bridge CLIs that agents depend on for durable access to external chat
surfaces.

Bridges in scope:

- `wacli` — WhatsApp sidecar
- `tgcli` — Telegram sidecar
- `imsg` — iMessage/SMS sidecar

This workflow is designed for a public repo and must stay reusable. Never hardcode phone
numbers, chat IDs, bot tokens, usernames, hostnames, or private paths beyond generic
home-directory patterns.

You run in one of two modes based on the triggering message:

1. **healthcheck** — verify bridge health and alert only on problems
2. **update-check** — check installed vs upstream/current versions and alert only on
   meaningful drift

Be fast, autonomous, and quiet when things are fine.

## Definition of Done

### Verification Level: B (self-score + circuit breakers)

Infrastructure monitoring with alerting and lightweight remediation — false negatives
miss real outages, false positives page the admin unnecessarily, and poor dedup floods
the channel with repeat alerts. Self-scoring catches quality drift across runs.

### Completion Criteria

- All configured bridges on this host were checked independently
- Each bridge status was normalized to healthy/degraded/down with severity
- Failure signatures were compared against `CLAUDE.local.md` for dedup
- Only genuinely new or changed incidents triggered alerts
- Healthy hosts produced exactly `HEARTBEAT_OK` and zero notifications
- `CLAUDE.local.md` was updated with current incident fingerprints
- Log file was written (healthcheck mode: `logs/YYYY-MM-DD-healthcheck.md`, update-check
  mode: `logs/YYYY-MM-DD-update-check.md`)

### Output Validation

- Every alert includes: bridge name, severity, concise diagnosis, suggested next action
- No duplicate alerts for unchanged incidents (dedup working)
- No alerts for bridges not configured on this host
- Suggested actions match the failure signature (not generic advice)
- `HEARTBEAT_OK` is only returned when ALL configured bridges are truly healthy

### Quality Rubric

| Dimension          | ⭐                             | ⭐⭐                        | ⭐⭐⭐                         | ⭐⭐⭐⭐                                 | ⭐⭐⭐⭐⭐                              |
| ------------------ | ------------------------------ | --------------------------- | ------------------------------ | ---------------------------------------- | --------------------------------------- |
| Detection coverage | Skipped a configured bridge    | Checked some bridges        | All configured bridges checked | All checked with correct status          | All checked + caught subtle degradation |
| Alert accuracy     | Alerted on healthy bridges     | Some false positives        | Alerts match real issues       | Zero false positives, zero missed issues | Accurate + actionable suggested fix     |
| Dedup quality      | No dedup, repeated every alert | Some dedup but inconsistent | Dedup works for exact matches  | Dedup handles signature evolution        | Dedup + clears resolved incidents       |

---

## EXEC RULES (CRITICAL)

**NEVER use shell heredoc syntax** (`<< 'EOF'`, `<<EOF`, `<< HEREDOC`, etc.) in any exec
command. The gateway blocks these as obfuscation. Instead:

- Use the `write` tool to create script files, then execute them separately
- Or break complex logic into individual direct commands
- Or use `echo "line1\nline2" > file` for small files

**NEVER write scripts longer than 10,000 characters** in a single exec command.

Violating these rules causes approval timeouts that spam the user.

## Local State: CLAUDE.local.md

Use `CLAUDE.local.md` in the current repo as private machine-local context.

If it exists and is readable, read it first. If it does not exist, is empty, or is stale
(>7 days old), do a lightweight discovery and write/update it.

Keep `CLAUDE.local.md` factual and machine-specific. It is gitignored and may contain:

- which bridges are installed on this host
- which bridges are intentionally configured on this host
- key state locations (for example `~/.wacli`, `~/.tgcli`)
- whether a long-lived sync/service is expected (`wacli sync --follow`, scheduled
  `tgcli sync`, etc.)
- last successful healthcheck and update-check timestamps
- active incident fingerprints to avoid duplicate alerts

Do **not** put secrets, raw logs, or personal IDs in `CLAUDE.local.md`.

**Failures & Corrections section:** Track cases where alerts were wrong, dedup failed,
or status was misclassified. Include this section in `CLAUDE.local.md`:

```markdown
## Failures & Corrections

- [date]: Alerted wacli down but was actually a transient disconnect. Next time: retry
  after 30s before alerting.
- [date]: Missed tgcli degraded state — store was stale but reads still worked. Next
  time: check mtime on store file.
```

**Active guardrail:** Before checking any bridges, read `CLAUDE.local.md` and check the
Failures & Corrections section. If a current bridge status matches a previously
corrected pattern, apply the corrected diagnostic approach instead of repeating the
mistake.

## Notification Routing

This workflow is in the **admin lane**. Notify via `~/.openclaw/health-check-admin` if
action is required.

The cron jobs for this workflow must use `delivery.mode: "none"`. Handle notifications
yourself only when something is wrong.

## Severity Model

- **P1** — bridge down, auth broken, permissions broken, or outdated client blocking
  live use
- **P2** — degraded or stale data, process dead but recoverable, local cache too old,
  sync not running when expected
- **P3** — update available only; no current outage

## Health Model by Bridge

### wacli

Healthy when:

- `wacli` binary exists
- `wacli doctor` succeeds
- `AUTHENTICATED true`
- `CONNECTED true`
- if this host expects a long-lived sync, the `wacli sync --follow` process is running
- no recent `Client outdated (405)` signature in the sync log

Degraded when:

- authenticated but disconnected
- sync process is absent but reads still work
- local state exists but recent sync activity looks stale

Down when:

- not authenticated
- `Client outdated (405)` appears recently
- the CLI fails basic reads or doctor reports hard failure

### tgcli

Healthy when:

- `tgcli` binary exists
- the local store is readable
- a basic live read works, such as `tgcli chat ls --limit 1 --json`

Degraded when:

- auth appears valid but local cache/store is stale
- the CLI works inconsistently or only offline/local reads succeed

Down when:

- not logged in
- store is unreadable/corrupt
- a basic read fails consistently

### imsg

Healthy when:

- `imsg` binary exists
- `imsg chats` succeeds
- Messages data is readable and permissions are intact

Degraded when:

- CLI exists but returns permission or automation errors intermittently

Down when:

- Messages access is denied
- Messages DB access or Apple automation is blocked
- basic CLI reads fail consistently

## First-Run / Discovery

On first run, discover which bridges are present on this host. Use lightweight checks
only:

- `command -v wacli`, `command -v tgcli`, `command -v imsg`
- whether `~/.wacli` / `~/.tgcli` exist
- whether a long-lived `wacli sync --follow` process exists
- whether `imsg chats --limit 1` works on this machine

Infer a host bridge set conservatively:

- `wacli` is configured if the binary exists and `~/.wacli` exists
- `tgcli` is configured if the binary exists and `~/.tgcli` exists
- `imsg` is configured if the binary exists on macOS

Write the discovered bridge set to `CLAUDE.local.md` and only check configured bridges
in future runs. If a bridge is absent and not configured, skip it silently.

## Mode 1: Healthcheck

When the triggering message indicates healthcheck mode:

1. Read `CLAUDE.local.md` if present.
2. Determine the configured bridges for this host.
3. Check each configured bridge independently. One failure must not block the others.
4. For each bridge, normalize results into:
   - `status`: healthy | degraded | down
   - `severity`: P1 | P2 | P3 | none
   - `failure_signature`
   - `suggested_action`
5. Deduplicate alerts using an incident fingerprint in `CLAUDE.local.md`. Do not resend
   the same unchanged alert every run.
6. If all configured bridges are healthy, reply exactly `HEARTBEAT_OK`.

### Required checks

#### wacli

Run these, as applicable:

- `wacli --version`
- `wacli doctor`
- `wacli chats list --limit 1 --json`
- `pgrep -fal "wacli sync --follow"`
- inspect recent log lines from `~/.wacli/sync.log` for:
  - `Client outdated`
  - repeated websocket/connect failures

#### tgcli

Run these, as applicable:

- `tgcli --version`
- `tgcli chat ls --limit 1 --json`
- optionally inspect `~/.tgcli/tgcli.db` mtime for cache staleness context

#### imsg

Run these, as applicable:

- `imsg --version`
- `imsg chats --limit 1`

### Healthcheck alert rules

Alert only when:

- a configured bridge is down
- a configured bridge is degraded in a way that likely affects workflows
- a failure signature changed since the last alert

The alert must include:

- bridge name
- severity
- concise diagnosis
- suggested next action

Suggested next actions:

- `wacli` outdated → upgrade binary first, then re-auth only if still needed
- `wacli` not authenticated → re-auth
- `tgcli` auth/store broken → login or repair store
- `imsg` permissions issue → restore Messages / automation permissions

## Mode 2: Update Check

When the triggering message indicates update-check mode:

1. Read `CLAUDE.local.md` if present.
2. Check only configured bridges.
3. Compare installed version vs a reasonable upstream/current reference.
4. Alert only if drift is meaningful.
5. Never auto-update.
6. If no meaningful drift exists, reply exactly `HEARTBEAT_OK`.

### Update policy

- Daily healthcheck catches outages.
- Weekly update-check catches drift.
- Do **not** auto-upgrade fragile bridges.
- Prefer canary/manual promotion over blind updates.

### Update-check guidance by bridge

#### wacli

- record installed version via `wacli --version`
- compare against Homebrew stable and/or upstream release/commit metadata if available
- if current outage matches `Client outdated`, treat available newer build as
  P1-relevant, otherwise P3

#### tgcli

- record installed version via `tgcli --version`
- compare against installed source/release if available

#### imsg

- record installed version via `imsg --version`
- compare against package manager status if available

## Failure Signatures

Track and recognize these common patterns:

- `wacli-outdated-405`
- `wacli-auth-lost`
- `wacli-sync-missing`
- `tgcli-not-logged-in`
- `tgcli-store-unreadable`
- `tgcli-stale-cache`
- `imsg-permissions`
- `imsg-cli-failure`

Update `CLAUDE.local.md` with the current incident fingerprint and clear it when
resolved.

## Circuit Breakers

If 3 consecutive healthcheck runs score below ⭐⭐⭐ on any rubric dimension, alert the
admin via `~/.openclaw/health-check-admin` with:

- Which dimension is failing (detection, alerts, or dedup)
- The last 3 scores and what went wrong
- Whether the issue is host-specific (bridge changed behavior) or workflow-level

While in a circuit-breaker state, continue checking bridges but do not attempt any
lightweight remediation (process restarts, log rotation). Report-only mode until the
admin acknowledges.

## Recovery Order

Healthcheck mode may do **lightweight, safe** remediation only when clearly reversible:

- restart a missing long-lived bridge process if this host's notes say it should be
  running and the restart command is already documented in `CLAUDE.local.md`
- trim or rotate an oversized local log

Do **not**:

- re-auth interactively
- delete auth state
- upgrade packages automatically
- invent restart commands that are not already documented locally

If a bridge needs interactive auth, manual upgrade, or uncertain recovery, alert and
stop.

## Logs

Write one log per run: `logs/YYYY-MM-DD-healthcheck.md` or
`logs/YYYY-MM-DD-update-check.md`. Delete logs older than 30 days.

Each log file must end with a scorecard:

```markdown
## Scorecard

| Dimension          | Score      | Notes                                      |
| ------------------ | ---------- | ------------------------------------------ |
| Detection coverage | ⭐⭐⭐⭐⭐ | All 3 configured bridges checked           |
| Alert accuracy     | ⭐⭐⭐⭐   | Correct P2 alert for stale tgcli           |
| Dedup quality      | ⭐⭐⭐⭐⭐ | Suppressed repeat wacli-sync-missing alert |
```

Be honest in self-scoring. The circuit breaker watches these scores.

## Output Discipline

- Healthy: reply exactly `HEARTBEAT_OK`
- Problem found: notify admin via `~/.openclaw/health-check-admin`, then reply with a
  short summary
- Never include PII, tokens, IDs, or machine-private routing details in user-facing text

## Suggested Cron Jobs

### Bridge Healthcheck

Suggested schedule: every 3 hours during business hours, weekdays. Example:

```bash
openclaw cron add \
  --name "bridge-healthcheck" \
  --cron "0 8,11,14,17 * * 1-5" \
  --tz "America/Chicago" \
  --session isolated \
  --no-deliver \
  --timeout-seconds 120 \
  --message "Run the bridge health workflow in healthcheck mode. Read workflows/bridge-health/AGENT.md and follow it."
```

### Bridge Update Check

Suggested schedule: weekly. Example:

```bash
openclaw cron add \
  --name "bridge-update-check" \
  --cron "0 10 * * 1" \
  --tz "America/Chicago" \
  --session isolated \
  --no-deliver \
  --timeout-seconds 180 \
  --message "Run the bridge health workflow in update-check mode. Read workflows/bridge-health/AGENT.md and follow it."
```

On hosts with a non-standard workspace layout (no `~/.openclaw/workspace/` CWD), pass an
absolute path in `--message` instead of the relative `workflows/bridge-health/AGENT.md`.
Add `--model <alias>` only if the target host has that alias configured.

## Deployment

This file is the reusable public contract. Host-specific paths, restart commands, bridge
ownership, and alert dedupe state belong in `CLAUDE.local.md`, not here.

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

**Mode selection rule:** If the triggering message contains the substring
`update-check`, run Mode 2. Otherwise run Mode 1 (healthcheck).

Be fast, autonomous, and quiet when things are fine.

## EXEC RULES (CRITICAL)

**NEVER use shell heredoc syntax** (`<< 'EOF'`, `<<EOF`, `<< HEREDOC`, etc.) in any exec
command. The gateway blocks these as obfuscation. Instead:

- Use the `write` tool to create script files, then execute them separately
- Or break complex logic into individual direct commands
- Or use `echo "line1\nline2" > file` for small files

**NEVER write scripts longer than 10,000 characters** in a single exec command.

**Wrap every bridge CLI invocation with a per-command timeout when possible.** On macOS,
`gtimeout` (from `brew install coreutils`) is preferred — use
`gtimeout 15 wacli doctor`. If `gtimeout` is absent, proceed without it and rely on the
cron timeout as the outer bound, but **check which bridge you're on first** and probe
the cheap ones before the potentially-slow ones so one hang doesn't starve the others.
If the run detects missing `gtimeout`, include a one-time "install coreutils for
stricter timeouts" note in the alert or log (not a P-level incident).

Violating these rules causes approval timeouts that spam the user.

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

## Local State: CLAUDE.local.md

Use `CLAUDE.local.md` in the current repo as private machine-local context.

If it exists and is readable, read it first. If it does not exist, is empty, or is stale
(>7 days old), do a lightweight discovery and write/update it.

Keep `CLAUDE.local.md` factual and machine-specific. It is gitignored. Use the section
structure below so that dedup, restart gating, and circuit-breaker aggregation are
deterministic across runs.

### Required schema

```markdown
## Configured Bridges

- wacli: configured (sync-follow expected), state at `~/.wacli`, freshness window =
  latest-message within last 4h during 8am-10pm CT, last 12h overnight
- tgcli: configured, state at `~/.tgcli`, freshness window = latest-message within 6h
- imsg: configured, freshness window = n/a (SMS/iMessage is user-paced)

## Last Run Signals

<!-- Rewritten every run. Used by the restart-threshold rule. -->

- run: 2026-04-19T14:00-05:00
- wacli: [disconnected, reads-fail]
- tgcli: []
- imsg: []

## Active Incidents

<!-- Fingerprint = `<bridge>:<signature>:<severity>`. Cleared when resolved. -->

- wacli:wacli-composite-hang:P1 — first seen 2026-04-19T08:00, last alert
  2026-04-19T08:00

## Recent Scores

<!-- Last 3 runs. Used by the circuit breaker. -->

- 2026-04-19T14:00: detection=5, alerts=4, dedup=5
- 2026-04-19T11:00: detection=5, alerts=5, dedup=5
- 2026-04-19T08:00: detection=4, alerts=4, dedup=4

## Restart Commands

<!-- Hard gate for remediation. If a bridge isn't listed here, NEVER invent a restart. -->

- wacli (sync-follow): `launchctl kickstart -k gui/$(id -u)/ai.openclaw.wacli-sync`

## Failures & Corrections

<!-- Append-only. Read before diagnosis so past mistakes aren't repeated. -->

- 2026-04-19: Alerted wacli hung from quiet log alone — actually bursty sync. Require
  composite signals (reads + DB freshness + auth/connect) before calling a hang.
```

Do **not** put secrets, raw logs, or personal IDs in `CLAUDE.local.md`.

**Fail-closed on unreadable state:** If `CLAUDE.local.md` exists but is unparseable, run
in report-only mode for one cycle: check bridges, write a log, but send no alerts and
perform no remediation. Record in the log that dedup state was lost so the next run can
rebuild. Only alert when dedup state is confirmed consistent.

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

**Fallback when `~/.openclaw/health-check-admin` is missing or unreadable:** Do not
silently swallow the alert. Instead:

1. Write the full alert body (bridge, severity, diagnosis, suggested action) to
   `logs/YYYY-MM-DD-alert-UNDELIVERED.md`, appending if the file exists.
2. Prefix the workflow's reply text with `ALERT_UNDELIVERED:` so whatever tails cron
   output surfaces the condition rather than seeing a quiet run.
3. Include a one-line remediation hint (e.g., "create `~/.openclaw/health-check-admin`
   with the admin routing spec") in the reply.

Do not substitute a hardcoded channel/ID as fallback — this workflow ships in a public
repo and must stay PII-free.

## Severity Model

- **P1** — bridge down, auth broken, permissions broken, or outdated client blocking
  live use
- **P2** — degraded or stale data, process dead but recoverable, local cache too old,
  sync not running when expected
- **P3** — update available only; no current outage

## Health Model by Bridge

### wacli

Health is judged from **active probes**, never from filesystem mtime or log silence.
Quiet logs and stale mtime mean "no new traffic," not "bridge broken" — a bursty sync
can sit idle for an hour on purpose. Two primary signals carry the diagnosis:

1. **Liveness:** `wacli chats list --limit 1 --json` succeeds and returns a chat object.
2. **Forward progress:** the `.data[0].LastMessageTS` field on the returned chat
   (ISO-8601 UTC) falls inside the host's expected freshness window, taken from
   `## Configured Bridges` in `CLAUDE.local.md` (e.g., "latest-message within last 4h
   during 8am-10pm CT"). If the response shape is different on a given wacli build, fall
   back to whichever `*TS` / `*timestamp` / `updated_at` field is present — whichever
   one actually carries the latest message time — and note the field name in
   `## Configured Bridges` so future runs are deterministic.

Supplementary signals:

- `wacli doctor` → `AUTHENTICATED` and `CONNECTED` booleans (also `LOCKED` / `LOCK_INFO`
  confirms which pid owns the store)
- error-event count in the **live** log over roughly the last 5 minutes. Pick the live
  log by mtime: `~/.wacli/sync-error.log` is typically the running log; `sync.log` is
  often stale from a previous run. Select whichever file has the most recent mtime, then
  `tail -n 200` and count lines matching: `websocket`, `reconnect`, `401`,
  `store locked`, `timeout`, `Client outdated`. Log lines use bare `HH:MM:SS.mmm` with
  no date, so "last 5 minutes" is approximate — if the log's mtime is older than 10
  minutes, treat the error-window count as `0` (no recent activity = no recent errors).
- presence of the `wacli sync --follow` process on hosts where it's expected (via
  `pgrep -fal "wacli sync --follow"`)

Healthy when ALL of:

- binary exists, `wacli doctor` succeeds, `AUTHENTICATED true`
- live read succeeds on first attempt
- returned latest-message timestamp is within the host's freshness window
- windowed error-event count = 0
- if sync-follow is expected on this host, the process is running
- no `Client outdated (405)` in the last 5 minutes of logs

Degraded when live reads still succeed AND any of:

- `CONNECTED false` from doctor
- latest-message timestamp exceeds the freshness window (sync likely stuck; local cache
  still serves — real user impact on inbound latency)
- windowed error-event count ≥ 1 in the last 5 minutes (reconnect churn, lock
  contention, transient network hiccup)
- sync-follow is expected on this host but the process is absent

Down when any of:

- not authenticated
- `Client outdated (405)` in the last 5 minutes of logs
- live reads fail ≥ 2 out of 3 consecutive attempts
- `wacli doctor` reports hard failure AND live reads also fail

**Explicitly removed signals (and why):**

- filesystem mtime of `session.db` / `wacli.db` / `wacli.db-wal` — stale mtime just
  means no inbound messages arrived, not that sync is broken
- log quietness / log mtime — `wacli sync --follow` is intentionally bursty; quiet ≠
  stuck. Use windowed error-event counts instead.

### tgcli

Same active-probe principle as wacli: judge health from live reads, not from file mtime.
Run the live read ≥ 3 times when a single read behaves oddly, and count failures
explicitly.

Healthy when:

- `tgcli` binary exists
- `tgcli chat ls --json` succeeds on first attempt (fetch several chats, not just 1 —
  tgcli sort order is not recency-first and chat[0] can have a zero-value
  `last_message_ts`)
- the **maximum** `last_message_ts` across the returned chats, ignoring zero-value
  sentinels (`0001-01-01T00:00:00Z`, epoch-0, or empty), is within the host's freshness
  window (if configured in `## Configured Bridges`)

Degraded when live reads still work AND any of:

- latest-message timestamp exceeds the freshness window (cache is serving but sync is
  stuck)
- reads succeed but ≥ 1 of 3 consecutive attempts returned an error

Down when:

- auth check fails / not logged in
- store file is missing or returns I/O errors
- live read fails ≥ 2 of 3 consecutive attempts

### imsg

`imsg chats` output is **plain text**, not JSON. Lines look like
`[NNNN]  (+PHONE) last=2026-04-20T03:22:25.161Z` — extract the ISO-8601 timestamp after
`last=`. The phone number / handle is PII and must be redacted before it lands in any
alert body or log quote (see Output Discipline / Log-snippet redaction).

Healthy when:

- `imsg` binary exists
- `imsg chats --limit 1` succeeds on first attempt
- no permission or automation errors in the response
- the extracted `last=` timestamp is within the host's freshness window (if configured —
  imsg freshness is typically `n/a` since it's user-paced)

Degraded when:

- `imsg chats` succeeds but returns permission/automation warnings in ≥ 1 of 3
  consecutive attempts

Down when:

- Messages / Apple Events access is denied
- `imsg chats` fails ≥ 2 of 3 consecutive attempts with non-permission errors

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

**Zero-bridge host:** If discovery finds zero bridges configured on this host, reply
exactly `HEARTBEAT_OK` and write one log line stating "no bridges configured on this
host." Do not treat this as an error.

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
- `wacli doctor` (parse `AUTHENTICATED` and `CONNECTED` booleans)
- `wacli chats list --limit 1 --json` (parse latest-message timestamp from the returned
  chat; compare to the host's freshness window from `## Configured Bridges`)
- `pgrep -fal "wacli sync --follow"` (only if sync-follow is expected on this host)
- windowed error-event count: select the live log by mtime — `sync-error.log` is
  typically the running log; `sync.log` is often stale from a previous run — then
  `tail -n 200` it and count lines from the last 5 minutes containing any of
  `websocket`, `reconnect`, `401`, `store locked`, `timeout`, `Client outdated`

Interpretation order:

1. **Liveness** — if the live read succeeds, the bridge is serving. Silent logs and
   stale DB/WAL mtime are irrelevant.
2. **Auth state** — `AUTHENTICATED false` is a real outage. Down.
3. **Forward progress** — returned latest-message timestamp outside the freshness window
   means sync is stuck even though reads work. Degraded.
4. **Connectivity** — `CONNECTED false` with successful reads is Degraded, not Down.
5. **Error-event window** — ≥1 explicit error in the last 5 minutes is Degraded even if
   reads succeed (catches reconnect churn and lock contention that will eventually cause
   user impact).
6. **Restart threshold** — only recommend restart when at least two Down-severity
   signals agree for two consecutive runs, for example:
   - live-read-fail + auth-lost
   - live-read-fail + sync-process-missing (on a host where follow is expected)
   - `Client outdated (405)` + sustained read failure

The "two consecutive runs" check relies on the `## Last Run Signals` block in
`CLAUDE.local.md`. Read it before diagnosis; rewrite it every run with the current
bridge signal set. Without this persisted history, the threshold check is not meaningful
— if the block is missing, do not restart.

Do **not** restart `wacli` from a single-run signal or from log silence.

#### tgcli

Run these, as applicable:

- `tgcli --version`
- `tgcli chat ls --limit 5 --json` (fetch several chats — sort order is not
  recency-first, so take the max `last_message_ts` across results, ignoring zero-value
  sentinels)
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
- `wacli` degraded but basic reads succeed → monitor, do not restart just for quiet logs
- `wacli` composite hang signals confirmed across consecutive runs → restart the sync
  service once, then verify reads and freshness
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

One diagnosis → exactly one signature. Check in precedence order and stop at the first
match; this keeps fingerprints deterministic across runs so dedup actually works.

### wacli precedence

| #   | Signature                        | Condition                                                                         | Severity |
| --- | -------------------------------- | --------------------------------------------------------------------------------- | -------- |
| 1   | `wacli-outdated-405`             | `Client outdated (405)` appears in last 5 minutes of the live log                 | P1       |
| 2   | `wacli-auth-lost`                | `AUTHENTICATED false` from doctor                                                 | P1       |
| 3   | `wacli-composite-hang`           | live read fails ≥ 2 of 3 attempts AND `CONNECTED false` AND `LastMessageTS` stale | P1       |
| 4   | `wacli-read-fail`                | live read fails ≥ 2 of 3 attempts (auth intact, not outdated)                     | P1       |
| 5   | `wacli-stuck-sync`               | live read succeeds but `LastMessageTS` is older than the freshness window         | P2       |
| 6   | `wacli-sync-missing`             | sync-follow process is absent on a host that expects it, reads still succeed      | P2       |
| 7   | `wacli-disconnected-degraded`    | `CONNECTED false`, reads succeed, windowed error-count = 0                        | P2       |
| 8   | `wacli-reconnect-churn`          | windowed error-count ≥ 1, reads succeed, `CONNECTED true`                         | P2       |
| 9   | `wacli-disconnected-with-errors` | `CONNECTED false`, reads succeed, windowed error-count ≥ 1                        | P2       |

### tgcli precedence

| #   | Signature                | Condition                                                           | Severity |
| --- | ------------------------ | ------------------------------------------------------------------- | -------- |
| 1   | `tgcli-store-unreadable` | store file missing or I/O error on access                           | P1       |
| 2   | `tgcli-not-logged-in`    | auth check fails or `tgcli chat ls` returns unauthenticated error   | P1       |
| 3   | `tgcli-read-fail`        | live read fails ≥ 2 of 3 attempts (auth intact, store accessible)   | P1       |
| 4   | `tgcli-stale-cache`      | reads succeed but latest-message timestamp outside freshness window | P2       |

### imsg precedence

| #   | Signature          | Condition                                                              | Severity |
| --- | ------------------ | ---------------------------------------------------------------------- | -------- |
| 1   | `imsg-permissions` | Messages / Apple Events access denied (permission or automation error) | P1       |
| 2   | `imsg-cli-failure` | `imsg chats` fails ≥ 2 of 3 attempts with non-permission errors        | P1       |

Update the `## Active Incidents` block in `CLAUDE.local.md` with the current fingerprint
(`<bridge>:<signature>:<severity>`) and clear it when the matching condition no longer
holds.

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

**Pre-flight gate (hard requirement):** Before attempting any remediation, confirm that
`CLAUDE.local.md` has a `## Restart Commands` section that lists the exact bridge name
with a concrete command. If the section is missing, the bridge is not listed, or the
command is ambiguous, skip remediation entirely and alert only. **Never synthesize a
restart command.**

Healthcheck mode may do **lightweight, safe** remediation only when clearly reversible
AND the pre-flight gate passes:

- restart a missing long-lived bridge process, using the exact command from
  `## Restart Commands`
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
`logs/YYYY-MM-DD-update-check.md`. Delete logs older than 30 days using an idempotent
command that does not fail on a missing directory:

```bash
find logs/ -name '*.md' -mtime +30 -delete 2>/dev/null || true
```

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

**Mechanical cross-check:** If you reply `HEARTBEAT_OK` but any configured bridge was
skipped or errored mid-run (timeout, missing binary, exec failure), score **Detection
coverage at ⭐⭐ or lower** regardless of other signals. A clean heartbeat with missed
bridges is the exact failure the circuit breaker exists to catch.

After writing the scorecard, append the new row to the `## Recent Scores` block in
`CLAUDE.local.md` and keep only the most recent 3 rows.

## Output Discipline

- Healthy: reply exactly `HEARTBEAT_OK`
- Problem found: notify admin via `~/.openclaw/health-check-admin`, then reply with a
  short summary
- Never include PII, tokens, IDs, or machine-private routing details in user-facing text

**Log-snippet redaction:** Bridge logs (wacli, tgcli) routinely contain phone numbers,
chat IDs, bot tokens, and JIDs. Before quoting any log line in an alert or log file,
redact these patterns:

- phone numbers: `\+?\d{10,}` → `[PHONE]`
- Telegram chat IDs: `-?\d{9,}` → `[TG_ID]`
- bot tokens: `\d+:[A-Za-z0-9_-]{20,}` → `[TOKEN]`
- WhatsApp JIDs: `@s\.whatsapp\.net` or `@g\.us` → `[JID]`

If redaction is uncertain, **summarize the log content in prose instead of quoting it.**

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

---
name: 9router-health
version: 0.1.0
description:
  Health monitoring for a host-local 9router proxy with private host gating via
  CLAUDE.local.md
---

# 9router Health

You monitor a host-local 9router proxy that agents depend on for LLM routing.

This workflow is designed for a public repo and must stay reusable. Never hardcode IPs,
hostnames, launchd labels, private filesystem paths beyond generic home-directory
patterns, chat IDs, tokens, or raw log content.

Be fast, autonomous, and quiet when things are fine.

## EXEC RULES (CRITICAL)

**NEVER use shell heredoc syntax** (`<< 'EOF'`, `<<EOF`, `<< HEREDOC`, etc.) in any exec
command. The gateway blocks these as obfuscation. Instead:

- Use the `write` tool to create script files, then execute them separately
- Or break complex logic into individual direct commands
- Or use `echo "line1\nline2" > file` for small files

**NEVER write scripts longer than 10,000 characters** in a single exec command.

**Wrap every probe with a per-command timeout when possible.** On macOS, `gtimeout`
(from `brew install coreutils`) is preferred. If `gtimeout` is absent, proceed without
it and rely on the cron timeout as the outer bound, but check the cheapest probes first
so one hang does not starve the rest of the run.

## Performance Budget

A normal configured-host run should finish in **5 seconds or less**. Treat that as a
budget, not an aspiration:

- Applicability parse from `CLAUDE.local.md`: target < 250 ms
- Listening-port probe: target < 1 s
- `/api/health` probe: timeout at 2 s when `gtimeout` is available
- Recent stderr/log scans: bounded tail windows only; never scan entire large logs
- Log directory size check: one bounded `du -sk` / `du -sm` command, no recursive
  analysis
- Alert delivery: only after probes finish and only for new/changed incidents

If a run cannot stay under 5 seconds because local logs are too large, record a P3
`9router-log-bloat` finding and tighten the scanned window rather than letting the
health check become the outage.

## Definition of Done

### Verification Level: B (self-score + circuit breakers)

Infrastructure monitoring with alerting and lightweight diagnosis — false negatives miss
real outages, false positives page the admin unnecessarily, and poor dedup floods the
channel with repeat alerts.

### Completion Criteria

- The workflow first determines whether 9router is configured on this host
- Non-9router hosts produce exactly `HEARTBEAT_OK`, write a short not-applicable log,
  and send no notifications
- Configured 9router hosts run cheap local probes, normalize status to healthy /
  degraded / down, and map findings to the severity model below
- Failure signatures are compared against `CLAUDE.local.md` for dedup before alerting
- Only genuinely new or changed incidents trigger alerts
- Healthy configured hosts produce exactly `HEARTBEAT_OK` and zero notifications
- `CLAUDE.local.md` is updated with current incident fingerprints
- A log file is written at `logs/YYYY-MM-DD-healthcheck.md`

### Output Validation

- Every alert includes: signature, severity, concise diagnosis, suggested next action
- No duplicate alerts for unchanged incidents
- No alerts for hosts without a configured 9router block
- `HEARTBEAT_OK` is returned only when the host is either not applicable or truly
  healthy

### Quality Rubric

| Dimension               | ⭐                             | ⭐⭐                | ⭐⭐⭐                              | ⭐⭐⭐⭐                                | ⭐⭐⭐⭐⭐                                                      |
| ----------------------- | ------------------------------ | ------------------- | ----------------------------------- | --------------------------------------- | --------------------------------------------------------------- |
| Applicability detection | Probed every host the same way | Some host gating    | Non-9router hosts skipped correctly | Correct skip + log discipline           | Correct skip + no false alerts                                  |
| Detection coverage      | Missed major failures          | Checks some signals | Checks all core signals             | Checks all core signals with thresholds | Checks signals + distinguishes degraded vs user-visible failure |
| Dedup quality           | No dedup                       | Some dedup          | Exact-match dedup works             | Dedup handles changed fingerprints      | Dedup + clears resolved incidents                               |

## Circuit Breakers

Use the self-score in `CLAUDE.local.md` as an operational safety brake, not decoration.

- After each configured-host run, record applicability / detection / dedup scores from
  1–5 under `## Recent Scores`
- If **3 consecutive configured-host runs** score below ⭐⭐⭐ in any dimension, enter
  report-only mode for the next run: probe and log normally, but send no alerts and do
  not mutate incident fingerprints except to record the circuit-breaker state
- If report-only mode produces a ⭐⭐⭐ or better score in every dimension, resume
  normal alerting on the following run
- If report-only mode still scores below ⭐⭐⭐, keep report-only mode and write the
  exact failing dimension(s) to the log
- Never use circuit breakers to suppress P1 process-down or health-endpoint-down facts
  from the log; the breaker only suppresses outbound alert delivery while the workflow
  is proving itself unreliable

## Local State: CLAUDE.local.md

Use `CLAUDE.local.md` in the current repo as private machine-local context.

If it exists and is readable, read it first. If it does not exist, is empty, or lacks
the `## 9router` block, treat this host as not applicable unless a human has provided
the required local values. Do not invent or overwrite 9router configuration from
lightweight discovery.

Keep `CLAUDE.local.md` factual and machine-specific. It is gitignored.

### Required schema

`CLAUDE.local.md` must provide a `## 9router` block with these keys:

- `installed: true`
- `port: <local-port>`
- `base_url: http://<host-or-ip>:<port>`
- `log_dir: ~/path/to/9router/logs`
- `restart_command: <local-service-restart-command>`
- `stderr_log: ~/path/to/stderr.log`
- `log_bloat_threshold_gb: <number>`

Example shape only:

```markdown
## 9router

- installed: true
- port: <local-port>
- base_url: http://<host-or-ip>:<port>
- log_dir: ~/path/to/9router/logs
- restart_command: <local-service-restart-command>
- stderr_log: ~/path/to/stderr.log
- log_bloat_threshold_gb: <number>

## Last Run Signals

- run: <timestamp>
- process: listening
- health: 200
- stream_sample: <number>
- stream_failures: <number>
- anthropic_429_hits: <number>

## Active Incidents

- 9router:<signature>:<severity> — first seen <timestamp>, last alert <timestamp>

## Recent Scores

- <timestamp>: applicability=5, detection=5, dedup=5

## Failures & Corrections

- <date>: Quiet logs alone are not enough to call the service stuck. Require failed
  active probes or other corroborating error signals.
```

If the `## 9router` block is absent or `installed` is not true, treat this host as not
applicable: write a short log line and return exactly `HEARTBEAT_OK`.

Do **not** put secrets, raw logs, personal names, private IDs, or raw stderr excerpts in
`CLAUDE.local.md`.

## First-Run / Discovery

9router configuration is manually supplied host-local state. Unlike generic service
discovery, the workflow cannot safely infer `base_url`, `log_dir`, `stderr_log`,
`restart_command`, or `log_bloat_threshold_gb`.

Allowed first-run behavior:

- If `CLAUDE.local.md` is missing, empty, or lacks `## 9router`, write a short
  not-applicable log and return exactly `HEARTBEAT_OK`
- If `## 9router` exists but required keys are missing, run report-only for one cycle,
  write which keys are missing to the workflow log, send no alerts, and do not mutate
  the local config
- If `installed: false` or `installed` is absent, treat the host as not applicable
- If the block is complete, use only those configured values for probes

Do not refresh config based on age alone. Stale timestamps may be noted in logs, but
manual host configuration remains authoritative until a human changes it.

**Fail-closed on unreadable state:** If `CLAUDE.local.md` exists but is unparseable, run
in report-only mode for one cycle: probe, write a log, but send no alerts and perform no
remediation.

## Notification Routing

This workflow is in the **admin lane**. Notify via `~/.openclaw/health-check-admin` if
action is required.

The cron jobs for this workflow must use `delivery.mode: "none"`. Handle notifications
yourself only when something is wrong.

**Fallback when `~/.openclaw/health-check-admin` is missing or unreadable:**

1. Write the full alert body to `logs/YYYY-MM-DD-alert-UNDELIVERED.md`, appending if the
   file exists
2. Prefix the workflow reply with `ALERT_UNDELIVERED:`
3. Include a one-line remediation hint in the reply

Do not substitute a hardcoded channel or ID as fallback.

## Severity Model

- **P1** — process down, configured port not listening, health endpoint unreachable, or
  recent stream outcomes show user-visible failure
- **P2** — provider degraded but fallback still working, credential issue appears,
  regression signature appears, or moderate stream failure ratio under a sufficient
  sample
- **P3** — log bloat, ambiguous idle/stuck indicators without corroborating failures, or
  advisory-only observations

## Health Model

Judge health in this order:

1. **Applicability gate** — `CLAUDE.local.md` says whether 9router is installed on this
   host and provides `port`, `base_url`, `log_dir`, and the local log file path(s)
2. **Process up** — local port is listening
3. **Service healthy** — `GET <base_url>/api/health` returns HTTP 200 within timeout
4. **Recent error signatures** — recent stderr/log window is scanned for known patterns
5. **Recent stream outcomes** — recent structured stream lines are sampled to estimate
   complete vs non-complete ratio
6. **Disk budget** — configured log directory size is compared with the local threshold

### Signatures

- `9router-process-down` — **P1**
  - Trigger: host is applicable and configured port is not listening
  - Suggested action: inspect local service manager state and restart manually if
    warranted

- `9router-local-probe-failed` — **P1**
  - Trigger: health endpoint cannot be reached within timeout or returns non-200
  - Suggested action: confirm bind address and inspect local stderr / launch logs

- `9router-stream-failures` — **P1** when sample size ≥ 50 and > 50% non-complete;
  otherwise **P2** when sample size ≥ 50 and failure ratio is elevated but not majority
  - Suggested action: inspect recent upstream/provider failures and compare with
    fallback behavior

- `9router-anthropic-429-storm` — **P2**
  - Trigger: more than 100 matching 429 / `rate_limit_error` signatures in the recent
    stderr window
  - Suggested action: confirm fallback paths are still completing and watch for
    user-visible stream failures

- `9router-credential-404` — **P2**
  - Trigger: `No active credentials for provider: claude` appears in the recent stderr
    window
  - Suggested action: restore provider credentials on the local host and re-run the
    health check

- `9router-temperature-deprecate` — **P2**
  - Trigger: `temperature is deprecate` appears in the recent stderr window
  - Suggested action: inspect whether the upstream patch regressed and compare with
    known-good fork state

- `9router-log-bloat` — **P3**
  - Trigger: configured log directory exceeds the locally documented threshold
  - Suggested action: inspect retention/rotation and prune only with explicit approval

- `9router-stuck-or-idle-ambiguous` — **P3**, report-only initially
  - Trigger: process is up but there is little or no recent log activity without failed
    active probes
  - Suggested action: do not page from silence alone; corroborate with health probe or
    stream failures first

## Detection Notes

- Prefer `lsof -nP -iTCP:<port> -sTCP:LISTEN` for the cheap local listening probe
- Prefer the explicit `/api/health` endpoint over token-spending live model requests
- The host-local `base_url` must come from `CLAUDE.local.md`; do not assume loopback
- Quiet logs alone are not enough to call the service broken
- Log scanning should use a bounded recent window only; summarize counts, not raw lines

## Logging

Write a concise log file at `logs/YYYY-MM-DD-healthcheck.md` for every run.

Each log should include:

- applicability result
- key probe results
- signature counts used for decisions
- final normalized status
- any alert sent or deduped
- self-score line for applicability / detection / dedup

Do not copy raw stderr blocks into the log. Summaries and counts only.

### Log Retention

Keep workflow-owned health logs bounded. Once per run, prune only this workflow's
markdown logs older than 30 days:

- Preferred command: `find logs -name '*.md' -mtime +30 -delete`
- If deletion fails, record `log-retention-prune-failed` as a P3 advisory in the run log
  and continue; do not let retention cleanup block health detection
- Do not prune host service logs or any path outside `workflows/9router-health/logs/`

## Remediation Posture

This workflow is detect-and-alert first.

Do not restart 9router automatically unless a future host-local policy explicitly says
to do so. If no restart policy is present, alert with the diagnosis and suggested next
step only.

## Suggested Cron Job

Run on a 30-minute cadence, matching the existing health-check family.

- schedule: `*/30 * * * *`
- delivery: `mode: "none"`
- invoke this workflow in healthcheck mode
- rely on admin-lane routing for alerts

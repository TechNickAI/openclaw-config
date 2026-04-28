# Agent Notes

## Patterns Observed

- 2026-04-19: On machine-1, `wacli doctor` returned `AUTHENTICATED true` +
  `CONNECTED false` while live reads succeeded with a fresh `LastMessageTS` (~8 min
  old). The old model would have flagged this as Down; the active-probe model correctly
  classifies it as Degraded-P2 (monitor only). Do not restart on `CONNECTED false` alone
  when the data plane is serving fresh messages.
- 2026-04-19: wacli JSON response shape on this host: `.data[0].LastMessageTS` (ISO-8601
  UTC, e.g. `2026-04-20T02:53:58Z`). Use that field for forward-progress checks.
- 2026-04-19: wacli live log is `~/.wacli/sync-error.log` (despite the name), not
  `sync.log`. `sync.log` is often stale from the previous sync run. Select the live log
  by mtime, not by filename.
- 2026-04-19: tgcli `chat ls --json` does **not** sort by recency. chat[0] can have
  `last_message_ts = 0001-01-01T00:00:00Z` (zero sentinel). Fetch several chats and take
  the max timestamp, ignoring zero values.
- 2026-04-19: imsg `chats` returns **plain text**, not JSON:
  `[NNNN]  (+PHONE) last=<ISO8601>`. Phone numbers appear verbatim — must redact before
  quoting in any alert or log.

## Mistakes Made

- 2026-04-19: Do not infer a hung `wacli sync --follow` process from quiet log output
  alone. `sync --follow` is intentionally bursty. Use active probes (live read +
  returned-chat timestamp) plus windowed error counts in the live log; drop
  filesystem-mtime and log-silence heuristics entirely.

## Optimizations

- 2026-04-19: `gtimeout` is not present by default on macOS (needs
  `brew install coreutils`). On hosts without it, fall back to running without a
  per-command timeout and rely on the cron timeout as the outer bound. Order probes
  cheap-first (`command -v`, version, doctor) before potentially-slow ones (live read,
  log tail) so a single hang doesn't starve the other bridges.

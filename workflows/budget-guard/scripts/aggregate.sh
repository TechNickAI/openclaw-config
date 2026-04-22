#!/usr/bin/env bash
# budget-guard/scripts/aggregate.sh
#
# Phase 1: pull month-to-date LLM spend, grouped by cron_id and by agent label.
# Writes a single JSON blob to stdout. Safe to dry-run.
#
# Usage:
#   ./aggregate.sh [--dry-run]
#
# Assumes `openclaw` CLI is on PATH and has a `cost` subcommand with --json.
# If the subcommand is missing, falls back to reading
# ~/.openclaw/agents/*/sessions/*.jsonl and summing `estimatedCostUsd` fields.

set -euo pipefail

MONTH_START=$(date -v1d +%Y-%m-%d 2>/dev/null || date -d "$(date +%Y-%m-01)" +%Y-%m-%d)
TODAY=$(date +%Y-%m-%d)

# Preferred path: official CLI
if openclaw cost --help >/dev/null 2>&1; then
  openclaw cost --since "${MONTH_START}" --until "${TODAY}" --by cron --json
  exit 0
fi

# Fallback: walk session transcripts and sum estimatedCostUsd
SESS_DIR="${HOME}/.openclaw/agents"
if [[ ! -d "${SESS_DIR}" ]]; then
  echo '{"error":"no-session-data","month_start":"'"${MONTH_START}"'"}'
  exit 2
fi

python3 - <<'PY'
import json, os, sys, datetime, glob, re

home = os.path.expanduser("~")
month_start = datetime.date.today().replace(day=1)
totals_by_cron = {}
totals_by_agent = {}

for path in glob.glob(os.path.join(home, ".openclaw/agents/*/sessions/*.jsonl")):
    mtime = datetime.date.fromtimestamp(os.path.getmtime(path))
    if mtime < month_start:
        continue
    cron_id = None
    agent_label = None
    cost = 0.0
    try:
        with open(path, "r") as f:
            for line in f:
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if isinstance(row, dict):
                    if "estimatedCostUsd" in row:
                        try:
                            cost += float(row["estimatedCostUsd"])
                        except Exception:
                            pass
                    if not cron_id:
                        m = re.search(r"cron:([0-9a-f-]{36})", json.dumps(row))
                        if m:
                            cron_id = m.group(1)
                    if not agent_label:
                        lbl = row.get("label") or row.get("agent_label")
                        if lbl:
                            agent_label = lbl
    except Exception:
        continue
    if cost <= 0:
        continue
    if cron_id:
        totals_by_cron[cron_id] = totals_by_cron.get(cron_id, 0.0) + cost
    if agent_label:
        totals_by_agent[agent_label] = totals_by_agent.get(agent_label, 0.0) + cost

json.dump({
    "month_start": month_start.isoformat(),
    "generated_at": datetime.datetime.now().isoformat(),
    "by_cron": {k: round(v, 4) for k, v in totals_by_cron.items()},
    "by_agent": {k: round(v, 4) for k, v in totals_by_agent.items()},
}, sys.stdout, indent=2)
PY

#!/usr/bin/env python3
"""budget-guard/scripts/evaluate.py

Phase 2: read aggregate JSON on stdin, rules.md budgets (passed as --rules),
and produce a decision list on stdout.

Decision shape:
  {
    "ok":      [{"name":..., "spent":..., "cap":..., "pct":...}, ...],
    "warn":    [...],
    "breach":  [...],
    "essential_warn": [...],  # breach-level spend but listed as essential -> warn only
    "global": {"spent":..., "cap":..., "pct":..., "status":"ok|warn|breach"}
  }

Does not mutate anything. Safe to run anytime.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def parse_rules(rules_path: Path) -> dict:
    """Minimal YAML-ish parser for the fields we need, no external deps."""
    text = rules_path.read_text()
    out = {
        "global_cap": 200.0,
        "mode": "dry_run",
        "essential": [],
        "budgets": [],
        "agent_budgets": [],
    }
    m = re.search(r"global_monthly_cap_usd:\s*([0-9.]+)", text)
    if m:
        out["global_cap"] = float(m.group(1))
    m = re.search(r"^mode:\s*([a-z_]+)", text, re.MULTILINE)
    if m:
        out["mode"] = m.group(1)
    # essential list: lines in the Essential section starting with `- `
    in_essential = False
    for line in text.splitlines():
        if line.startswith("## Essential crons"):
            in_essential = True
            continue
        if in_essential and line.startswith("## "):
            in_essential = False
        if in_essential and line.strip().startswith("- "):
            out["essential"].append(line.strip()[2:].strip("`"))
    # budgets block (very small parser — expects already-simple yaml)
    in_budgets = False
    cur = None
    for line in text.splitlines():
        if "budgets:" in line and "agent_budgets" not in line:
            in_budgets = True
            continue
        if in_budgets and line.startswith("agent_budgets:"):
            in_budgets = False
        if in_budgets:
            s = line.strip()
            if s.startswith("- cron_id:"):
                if cur:
                    out["budgets"].append(cur)
                cur = {"cron_id": s.split(":", 1)[1].strip()}
            elif cur is not None and ":" in s and not s.startswith("- "):
                k, v = s.split(":", 1)
                cur[k.strip()] = v.strip().strip('"')
    if cur:
        out["budgets"].append(cur)
    return out


def is_essential(name: str, essentials: list[str]) -> bool:
    for pat in essentials:
        if pat in name or re.search(pat.replace("*", ".*"), name):
            return True
    return False


def classify(spent: float, cap: float) -> str:
    if cap <= 0:
        return "ok"
    pct = spent / cap
    if pct >= 1.0:
        return "breach"
    if pct >= 0.8:
        return "warn"
    return "ok"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", required=True)
    args = ap.parse_args()

    agg = json.load(sys.stdin)
    rules = parse_rules(Path(args.rules))

    decisions = {"ok": [], "warn": [], "breach": [], "essential_warn": []}
    for b in rules["budgets"]:
        cid = b.get("cron_id", "").strip()
        name = b.get("name", cid)
        cap = float(b.get("monthly_cap_usd", 0) or 0)
        spent = float(agg.get("by_cron", {}).get(cid, 0.0))
        status = classify(spent, cap)
        rec = {"cron_id": cid, "name": name, "spent": round(spent, 2),
               "cap": cap, "pct": round(spent / cap * 100, 1) if cap else 0}
        if status == "breach" and is_essential(name, rules["essential"]):
            rec["note"] = "essential — warn only"
            decisions["essential_warn"].append(rec)
        else:
            decisions[status].append(rec)

    total = sum(agg.get("by_cron", {}).values()) + sum(
        v for k, v in agg.get("by_agent", {}).items()
    )
    gcap = rules["global_cap"]
    decisions["global"] = {
        "spent": round(total, 2),
        "cap": gcap,
        "pct": round(total / gcap * 100, 1) if gcap else 0,
        "status": classify(total, gcap),
    }
    decisions["mode"] = rules["mode"]
    json.dump(decisions, sys.stdout, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

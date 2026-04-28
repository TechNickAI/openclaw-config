#!/usr/bin/env bash
# seed_watchlist.sh — Convenience wrapper to print the initial agent-platform
# watchlist as inbox entries, so synthesis has something to chew on even on a
# quiet day. Reads URLs from rules.md (agent-platforms source).
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$HOME/.openclaw/workspace}"
STATE_DIR="$WORKSPACE_ROOT/memory/ecosystem-intel"
INBOX="$STATE_DIR/inbox.jsonl"

mkdir -p "$STATE_DIR"
touch "$INBOX"

now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# Small hand-curated watchlist; rules.md is the real source of truth, but
# parsing YAML in bash is painful so we mirror the platform slugs here.
WATCHLIST=(
  "langchain-ai/langgraph"
  "coleam00/paperclip"
  "openai/openai-agents-python"
)

for slug in "${WATCHLIST[@]}"; do
  gh api "repos/$slug" 2>/dev/null \
    | jq -c --arg slug "$slug" --arg discovered "$(now_iso)" '
        {
          id: ("gh-repo:" + $slug),
          source_id: "agent-platforms",
          kind: "github_repo_snapshot",
          repo: $slug,
          title: (.full_name + " — " + (.description // "")),
          url: .html_url,
          stars: .stargazers_count,
          pushed_at: .pushed_at,
          published_at: .pushed_at,
          discovered_at: $discovered
        }
      ' >> "$INBOX" || true
done

echo "[ecosystem-intel/seed_watchlist] appended $(wc -l <"$INBOX" | tr -d ' ') total lines to $INBOX" >&2

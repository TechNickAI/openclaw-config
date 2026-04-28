#!/usr/bin/env bash
# harvest_github.sh — Pull latest releases and trending repos for ecosystem-intel.
#
# Appends JSON lines to memory/ecosystem-intel/inbox.jsonl. Idempotent: the
# filter phase dedupes against seen.json, so this script can run as often as
# the configured cadence without risk of duplicate findings.
#
# Requires: gh (authenticated), jq, date.
set -euo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-$HOME/.openclaw/workspace}"
STATE_DIR="$WORKSPACE_ROOT/memory/ecosystem-intel"
INBOX="$STATE_DIR/inbox.jsonl"

mkdir -p "$STATE_DIR/findings" "$STATE_DIR/briefs" "$STATE_DIR/proposals"
touch "$INBOX"

now_iso() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

# Releases: repo list comes from rules.md → sources (github_releases kind).
# For now we keep a small hardcoded allowlist; rules.md is the source of truth
# and a future iteration should parse it directly.
REPOS=(
  "openclaw/openclaw"
  "TechNickAI/openclaw-config"
  "anthropics/claude-code"
  "modelcontextprotocol/servers"
  "modelcontextprotocol/python-sdk"
  "openai/openai-agents-python"
  "langchain-ai/langgraph"
)

emit_release() {
  local repo="$1"
  # Use gh api for portability across older gh versions that lack `release list --json`.
  gh api "repos/$repo/releases?per_page=3" 2>/dev/null \
    | jq -c --arg repo "$repo" --arg discovered "$(now_iso)" '
        .[] | {
          id: ("gh-release:" + $repo + ":" + .tag_name),
          source_id: "openclaw-core",
          kind: "github_release",
          repo: $repo,
          title: (.name // .tag_name),
          url: .html_url,
          published_at: .published_at,
          discovered_at: $discovered
        }
      ' >> "$INBOX" || true
}

for repo in "${REPOS[@]}"; do
  emit_release "$repo"
done

# Report summary to stderr so cron logs stay readable.
echo "[ecosystem-intel/harvest_github] wrote to $INBOX ($(wc -l <"$INBOX" | tr -d ' ') total lines)" >&2

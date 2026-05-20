#!/bin/bash
# Apply the declarative Tailscale Serve + Funnel config in tailscale-serve.json.
#
# Single source of truth: tailscale-serve.json (next to this script).
# Edit that file, then run this script. Never run ad-hoc `tailscale serve ...`
# commands — they pile up and stomp each other.
#
# How this works:
#   1. Wait for tailscaled to be ready.
#   2. Parse the JSON config (huJSON: `//` line comments allowed).
#   3. Reset all current serve + funnel state (atomic clean slate).
#   4. Compile JSON -> `tailscale serve` / `tailscale funnel` commands.
#   5. Execute them.
#
# Why not `tailscale serve set-config`? That subcommand requires the newer
# multi-host Services abstraction (advertised to the tailnet). For a personal
# node we use the legacy per-node serve config, which has no native config-
# file interface. JSON remains the source of truth; the commands are derived.
#
# Run on boot by launchd: ~/Library/LaunchAgents/ai.openclaw.app-router-serve.plist
# Re-run any time you edit tailscale-serve.json.
#
# Persistence: tailscaled persists serve config to /Library/Tailscale/tailscaled.state
# across daemon restarts and reboots. The only thing that wipes it is an
# explicit `tailscale serve reset` (or `funnel reset`) call. Some external
# tools — including the OpenClaw gateway when configured with
# `gateway.tailscale.resetOnExit: true` — will call reset and clobber this
# config. Set `gateway.tailscale.mode: "off"` and `resetOnExit: false` in
# `~/.openclaw/openclaw.json` to disable that behavior. See README.md.
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"
TS="$(command -v tailscale)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="${TAILSCALE_SERVE_JSON:-$SCRIPT_DIR/tailscale-serve.json}"

if [ -z "$TS" ]; then
  echo "[apply-tailscale-serve] tailscale binary not found in PATH" >&2
  exit 1
fi
if [ ! -f "$SRC" ]; then
  echo "[apply-tailscale-serve] missing config: $SRC" >&2
  exit 1
fi

# Wait for tailscaled.
MAX_WAIT="${TAILSCALE_MAX_WAIT_SECS:-60}"
WAITED=0
until "$TS" status &>/dev/null; do
  sleep 2
  WAITED=$((WAITED + 2))
  if [ "$WAITED" -ge "$MAX_WAIT" ]; then
    echo "$(date): tailscaled never became ready, giving up" >&2
    exit 1
  fi
done

# Resolve this node's MagicDNS name and substitute into the config.
HOST="$("$TS" status --json | python3 -c '
import json, sys
s = json.load(sys.stdin)
name = (s.get("Self", {}).get("DNSName") or "").rstrip(".")
if not name:
    sys.exit("could not read DNSName from tailscale status")
print(name)
')"
echo "$(date): applying serve config for $HOST"

# Compile JSON -> shell commands. One command per line.
CMDS_FILE="$(mktemp -t ts-cmds.XXX.sh)"
trap 'rm -f "$CMDS_FILE"' EXIT

python3 - "$SRC" "$HOST" > "$CMDS_FILE" <<'PY'
import json, re, shlex, sys

src_path, host = sys.argv[1], sys.argv[2]
with open(src_path) as f:
    raw = f.read()

# Strip // line comments (huJSON -> JSON).
raw = re.sub(r"(^|\s)//[^\n]*", r"\1", raw)
raw = raw.replace("${HOST}", host)
cfg = json.loads(raw)

web = cfg.get("Web", {})
funnel_on = cfg.get("AllowFunnel", {})

def port_of(site, kind):
    if ":" not in site:
        sys.exit(f"{kind} key {site!r} must include a port (host:port)")
    return site.rsplit(":", 1)[1]

# Emit serve commands (one per path).
for site, site_cfg in web.items():
    port = port_of(site, "Web")
    handlers = site_cfg.get("Handlers", {})
    if not handlers:
        sys.exit(f"Web entry {site!r} has no Handlers")
    for path, handler in handlers.items():
        proxy = handler.get("Proxy")
        if not proxy:
            sys.exit(f"handler {site}{path} is missing Proxy upstream")
        if path == "/":
            print(f"tailscale serve --bg --https={port} {shlex.quote(proxy)}")
        else:
            print(f"tailscale serve --bg --https={port} --set-path={shlex.quote(path)} {shlex.quote(proxy)}")

# Emit funnel commands (replay each path on the funnel-enabled port).
for site, on in funnel_on.items():
    if not on:
        continue
    port = port_of(site, "AllowFunnel")
    site_cfg = web.get(site)
    if not site_cfg:
        sys.exit(f"AllowFunnel {site!r} has no matching Web entry")
    for path, handler in site_cfg.get("Handlers", {}).items():
        proxy = handler["Proxy"]
        if path == "/":
            print(f"tailscale funnel --bg --https={port} {shlex.quote(proxy)}")
        else:
            print(f"tailscale funnel --bg --https={port} --set-path={shlex.quote(path)} {shlex.quote(proxy)}")
PY

echo "$(date): compiled commands:"
sed 's/^/  /' "$CMDS_FILE"

# Reset, then replay.
"$TS" funnel reset >/dev/null 2>&1 || true
"$TS" serve  reset >/dev/null 2>&1 || true

bash -e "$CMDS_FILE" > /dev/null

echo "$(date): tailscale serve config applied"
"$TS" serve status
echo "--- funnel ---"
"$TS" funnel status

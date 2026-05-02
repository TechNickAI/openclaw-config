#!/bin/bash
# Idempotent install of the OpenClaw app router into ~/openclaw-apps/.
#
# Run from the repo root:
#   bash devops/app-router/scripts/install.sh
#
# Re-running is safe — existing files are not overwritten unless --force is set.
# After install, edit ~/openclaw-apps/ecosystem.config.js to set AUTH_SECRET and
# any per-app passwords, then start with:
#   pm2 start ~/openclaw-apps/ecosystem.config.js && pm2 save

set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${OPENCLAW_APPS_DIR:-$HOME/openclaw-apps}"
FORCE="${FORCE:-0}"
if [ "${1:-}" = "--force" ]; then FORCE=1; fi

copy_if_absent() {
    local src="$1" dst="$2"
    if [ -e "$dst" ] && [ "$FORCE" != "1" ]; then
        echo "  skip (exists): $dst"
    else
        cp -R "$src" "$dst"
        echo "  wrote: $dst"
    fi
}

echo "[install] source: $SRC"
echo "[install] target: $DEST"

mkdir -p "$DEST/_registry/logs"
copy_if_absent "$SRC/auth-service" "$DEST/auth-service"
copy_if_absent "$SRC/templates/ecosystem.config.js.example" "$DEST/ecosystem.config.js"
copy_if_absent "$SRC/templates/Caddyfile.example" "$DEST/_registry/Caddyfile"
copy_if_absent "$SRC/scripts/restore-tailscale-serve.sh" "$DEST/_registry/restore-tailscale-serve.sh"
chmod +x "$DEST/_registry/restore-tailscale-serve.sh"

echo "[install] installing auth-service deps"
(cd "$DEST/auth-service" && npm install --omit=dev --silent --no-audit --no-fund)

LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="ai.openclaw.app-router-serve.plist"
PLIST_DST="$LAUNCH_AGENT_DIR/$PLIST_NAME"
if [ -d "$LAUNCH_AGENT_DIR" ]; then
    if [ -e "$PLIST_DST" ] && [ "$FORCE" != "1" ]; then
        echo "  skip (exists): $PLIST_DST"
    else
        mkdir -p "$LAUNCH_AGENT_DIR"
        sed "s|<USER>|$USER|g" "$SRC/launchd/$PLIST_NAME" > "$PLIST_DST"
        echo "  wrote: $PLIST_DST"
        echo "  load with: launchctl bootstrap gui/\$(id -u) $PLIST_DST"
    fi
else
    echo "  skip launchd plist (not on macOS)"
fi

cat <<EOF

Next steps:
  1. Edit $DEST/ecosystem.config.js — set AUTH_SECRET (openssl rand -hex 32)
     and any APP_PASSWORD_<SLUG> / APP_TITLE_<SLUG> / APP_DESC_<SLUG> entries.
  2. Edit $DEST/_registry/Caddyfile to match.
  3. pm2 start $DEST/ecosystem.config.js && pm2 save
  4. pm2 start /opt/homebrew/bin/caddy --name caddy --interpreter none -- \\
       run --config $DEST/_registry/Caddyfile --adapter caddyfile
  5. tailscale serve --bg --https=4242 http://127.0.0.1:8080
EOF

#!/bin/bash
# Check if updates are available for openclaw-config

OPENCLAW_CACHE="${HOME}/.openclaw"
OPENCLAW_REPO="${OPENCLAW_CACHE}/repo"

if [ ! -d "$OPENCLAW_REPO" ]; then
    echo "❌ OpenClaw not installed. Run bootstrap.sh first."
    exit 1
fi

# Get installed version
if [ -f "$OPENCLAW_CACHE/installed-version" ]; then
    INSTALLED=$(cat "$OPENCLAW_CACHE/installed-version")
else
    INSTALLED="unknown"
fi

# Get local repo version
LOCAL=$(cat "$OPENCLAW_REPO/VERSION" 2>/dev/null || echo "unknown")

# Fetch latest without pulling
cd "$OPENCLAW_REPO"
git fetch origin --quiet
REMOTE=$(git show origin/main:VERSION 2>/dev/null || echo "unknown")
cd - > /dev/null

echo "OpenClaw Version Check"
echo ""
echo "Installed: $INSTALLED"
echo "Local:     $LOCAL"
echo "Remote:    $REMOTE"
echo ""

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "✓ Up to date"
    exit 0
else
    echo "⬆️  Update available!"
    echo ""
    echo "Run: openclaw sync"
    exit 1
fi

#!/bin/bash
set -e

echo "🐾 OpenClaw Config Bootstrap"
echo ""

# Determine OpenClaw directory
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/openclaw}"

if [ ! -d "$OPENCLAW_DIR" ]; then
    echo "⚠️  OpenClaw directory not found at $OPENCLAW_DIR"
    echo "   Set OPENCLAW_DIR environment variable to your openclaw directory"
    echo "   Example: OPENCLAW_DIR=~/my-openclaw ./bootstrap.sh"
    exit 1
fi

echo "✓ Found OpenClaw at: $OPENCLAW_DIR"
echo ""

# Check OS
OS="$(uname -s)"
if [[ "$OS" != "Darwin" && "$OS" != "Linux" ]]; then
    echo "❌ Error: This script only supports macOS and Linux."
    echo "Detected: $OS"
    exit 1
fi

echo "✓ Detected $OS"
echo ""

# Clone or update openclaw-config
OPENCLAW_CACHE="${HOME}/.openclaw"
OPENCLAW_REPO="${OPENCLAW_CACHE}/repo"

mkdir -p "$OPENCLAW_CACHE"

if [ ! -d "$OPENCLAW_REPO" ]; then
    echo "📥 Cloning openclaw-config..."
    git clone https://github.com/TechNickAI/openclaw-config.git "$OPENCLAW_REPO"
    echo "✓ Cloned successfully"
else
    echo "📥 Updating openclaw-config..."
    cd "$OPENCLAW_REPO"
    git pull
    cd - > /dev/null
    echo "✓ Updated to latest version"
fi

echo ""

# Track installation
VERSION=$(cat "$OPENCLAW_REPO/VERSION")
echo "$VERSION" > "$OPENCLAW_CACHE/installed-version"

# Copy files
echo "📋 Installing configuration..."

# AGENTS.md template
if [ ! -f "$OPENCLAW_DIR/AGENTS.md" ]; then
    cp "$OPENCLAW_REPO/templates/AGENTS.md" "$OPENCLAW_DIR/AGENTS.md"
    echo "✓ Created AGENTS.md"
else
    echo "⏭  AGENTS.md exists, skipping (use 'openclaw sync' to update)"
fi

# SOUL.md template
if [ ! -f "$OPENCLAW_DIR/SOUL.md" ]; then
    cp "$OPENCLAW_REPO/templates/SOUL.md" "$OPENCLAW_DIR/SOUL.md"
    echo "✓ Created SOUL.md (customize this!)"
else
    echo "⏭  SOUL.md exists, skipping"
fi

# USER.md template
if [ ! -f "$OPENCLAW_DIR/USER.md" ]; then
    cp "$OPENCLAW_REPO/templates/USER.md" "$OPENCLAW_DIR/USER.md"
    echo "✓ Created USER.md (customize this!)"
else
    echo "⏭  USER.md exists, skipping"
fi

# TOOLS.md template
if [ ! -f "$OPENCLAW_DIR/TOOLS.md" ]; then
    cp "$OPENCLAW_REPO/templates/TOOLS.md" "$OPENCLAW_DIR/TOOLS.md"
    echo "✓ Created TOOLS.md"
else
    echo "⏭  TOOLS.md exists, skipping"
fi

# HEARTBEAT.md template
if [ ! -f "$OPENCLAW_DIR/HEARTBEAT.md" ]; then
    cp "$OPENCLAW_REPO/templates/HEARTBEAT.md" "$OPENCLAW_DIR/HEARTBEAT.md"
    echo "✓ Created HEARTBEAT.md"
else
    echo "⏭  HEARTBEAT.md exists, skipping"
fi

# Memory directory structure
mkdir -p "$OPENCLAW_DIR/memory/people"
mkdir -p "$OPENCLAW_DIR/memory/projects"
mkdir -p "$OPENCLAW_DIR/memory/topics"
mkdir -p "$OPENCLAW_DIR/memory/decisions"

if [ ! -f "$OPENCLAW_DIR/memory/TASK-SYSTEM.md" ]; then
    cp "$OPENCLAW_REPO/memory/TASK-SYSTEM.md" "$OPENCLAW_DIR/memory/TASK-SYSTEM.md"
    echo "✓ Created memory/TASK-SYSTEM.md"
else
    echo "⏭  memory/TASK-SYSTEM.md exists, skipping"
fi

if [ ! -f "$OPENCLAW_DIR/memory/tasks.md" ]; then
    cp "$OPENCLAW_REPO/memory/tasks.md" "$OPENCLAW_DIR/memory/tasks.md"
    echo "✓ Created memory/tasks.md"
else
    echo "⏭  memory/tasks.md exists, skipping"
fi

if [ ! -f "$OPENCLAW_DIR/memory/heartbeat-state.json" ]; then
    cp "$OPENCLAW_REPO/memory/heartbeat-state.json" "$OPENCLAW_DIR/memory/heartbeat-state.json"
    echo "✓ Created memory/heartbeat-state.json"
else
    echo "⏭  memory/heartbeat-state.json exists, skipping"
fi

echo "✓ Memory directory structure ready"

# Skills directory
mkdir -p "$OPENCLAW_DIR/skills"

# Copy skills
for skill in limitless fireflies quo; do
    if [ ! -d "$OPENCLAW_DIR/skills/$skill" ]; then
        cp -r "$OPENCLAW_REPO/skills/$skill" "$OPENCLAW_DIR/skills/"
        chmod +x "$OPENCLAW_DIR/skills/$skill/$skill" 2>/dev/null || true
        echo "✓ Installed skill: $skill"
    else
        echo "⏭  Skill $skill exists, skipping"
    fi
done

# Install openclaw management skill
mkdir -p "$OPENCLAW_DIR/skills/openclaw"
cp "$OPENCLAW_REPO/skills/openclaw/SKILL.md" "$OPENCLAW_DIR/skills/openclaw/"
cp "$OPENCLAW_REPO/skills/openclaw/openclaw" "$OPENCLAW_DIR/skills/openclaw/"
chmod +x "$OPENCLAW_DIR/skills/openclaw/openclaw"
echo "✓ Installed openclaw management skill"

echo ""
echo "✨ Bootstrap complete!"
echo ""
echo "Installed version: $VERSION"
echo ""
echo "Next steps:"
echo "  1. Edit SOUL.md — define your AI's personality"
echo "  2. Edit USER.md — add your info"
echo "  3. Search/replace {{placeholders}} in AGENTS.md"
echo "  4. Configure API keys for skills you want to use:"
echo "     - LIMITLESS_API_KEY for Limitless Pendant"
echo "     - FIREFLIES_API_KEY for Fireflies.ai"
echo "     - QUO_API_KEY for Quo phone"
echo ""
echo "To sync updates later: openclaw sync"
echo ""

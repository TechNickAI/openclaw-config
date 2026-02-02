#!/bin/bash
set -e

# OpenClaw Sync Script
# Smart sync that preserves user modifications

OPENCLAW_CACHE="${HOME}/.openclaw"
OPENCLAW_REPO="${OPENCLAW_CACHE}/repo"
CLAWD_DIR="${CLAWDBOT_DIR:-$HOME/clawd}"
CHECKSUMS_FILE="${OPENCLAW_CACHE}/checksums.json"
CONFLICTS_LOG="${OPENCLAW_CACHE}/conflicts.log"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Sync openclaw-config updates to your Clawdbot installation.

Options:
  --force       Overwrite local changes with upstream
  --dry-run     Show what would change without modifying files
  --skills      Only sync skills
  --templates   Only sync templates
  -h, --help    Show this help

Examples:
  $(basename "$0")              # Smart sync
  $(basename "$0") --dry-run    # Preview changes
  $(basename "$0") --force      # Force overwrite
EOF
}

# Parse arguments
FORCE=false
DRY_RUN=false
SKILLS_ONLY=false
TEMPLATES_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skills)
            SKILLS_ONLY=true
            shift
            ;;
        --templates)
            TEMPLATES_ONLY=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check requirements
if [ ! -d "$CLAWD_DIR" ]; then
    echo "❌ Clawdbot directory not found: $CLAWD_DIR"
    echo "   Run bootstrap.sh first or set CLAWDBOT_DIR"
    exit 1
fi

if [ ! -d "$OPENCLAW_REPO" ]; then
    echo "❌ OpenClaw repo not found. Run bootstrap.sh first."
    exit 1
fi

echo "🔄 OpenClaw Sync"
echo ""

# Update repo
echo "📥 Fetching latest..."
cd "$OPENCLAW_REPO"
git fetch origin
LOCAL_VERSION=$(cat VERSION)
git pull
NEW_VERSION=$(cat VERSION)
cd - > /dev/null

if [ "$LOCAL_VERSION" = "$NEW_VERSION" ]; then
    echo "✓ Already at latest version: $NEW_VERSION"
else
    echo "✓ Updated: $LOCAL_VERSION → $NEW_VERSION"
fi
echo ""

# Load or initialize checksums
if [ -f "$CHECKSUMS_FILE" ]; then
    CHECKSUMS=$(cat "$CHECKSUMS_FILE")
else
    CHECKSUMS="{}"
fi

# Clear conflicts log
> "$CONFLICTS_LOG"

# Function to get file checksum
get_checksum() {
    local file="$1"
    if [ -f "$file" ]; then
        md5 -q "$file" 2>/dev/null || md5sum "$file" 2>/dev/null | cut -d' ' -f1
    else
        echo ""
    fi
}

# Function to get stored checksum
get_stored_checksum() {
    local key="$1"
    echo "$CHECKSUMS" | jq -r ".[\"$key\"] // \"\"" 2>/dev/null || echo ""
}

# Function to sync a file
sync_file() {
    local src="$1"
    local dst="$2"
    local key="$3"
    local category="$4"
    
    local src_checksum=$(get_checksum "$src")
    local dst_checksum=$(get_checksum "$dst")
    local stored_checksum=$(get_stored_checksum "$key")
    
    # Skip if filtered
    if [ "$SKILLS_ONLY" = true ] && [ "$category" != "skill" ]; then
        return
    fi
    if [ "$TEMPLATES_ONLY" = true ] && [ "$category" != "template" ]; then
        return
    fi
    
    # File doesn't exist locally - copy it
    if [ -z "$dst_checksum" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [NEW] $key"
        else
            mkdir -p "$(dirname "$dst")"
            cp "$src" "$dst"
            echo "  ✓ Created $key"
            # Store checksum
            CHECKSUMS=$(echo "$CHECKSUMS" | jq ". + {\"$key\": \"$src_checksum\"}")
        fi
        return
    fi
    
    # Source unchanged - nothing to do
    if [ "$src_checksum" = "$stored_checksum" ]; then
        return
    fi
    
    # User hasn't modified (checksum matches stored) - safe to update
    if [ "$dst_checksum" = "$stored_checksum" ] || [ -z "$stored_checksum" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [UPDATE] $key"
        else
            cp "$src" "$dst"
            echo "  ✓ Updated $key"
            CHECKSUMS=$(echo "$CHECKSUMS" | jq ". + {\"$key\": \"$src_checksum\"}")
        fi
        return
    fi
    
    # User has modified - conflict
    if [ "$FORCE" = true ]; then
        if [ "$DRY_RUN" = true ]; then
            echo "  [FORCE] $key (overwriting local changes)"
        else
            cp "$src" "$dst"
            echo "  ⚠️  Force updated $key (local changes overwritten)"
            CHECKSUMS=$(echo "$CHECKSUMS" | jq ". + {\"$key\": \"$src_checksum\"}")
        fi
    else
        echo "  ⚠️  CONFLICT: $key (local modifications preserved)"
        echo "$key" >> "$CONFLICTS_LOG"
    fi
}

# Sync templates
echo "📋 Checking templates..."
if [ "$SKILLS_ONLY" != true ]; then
    sync_file "$OPENCLAW_REPO/templates/AGENTS.md" "$CLAWD_DIR/AGENTS.md" "AGENTS.md" "template"
    sync_file "$OPENCLAW_REPO/templates/HEARTBEAT.md" "$CLAWD_DIR/HEARTBEAT.md" "HEARTBEAT.md" "template"
    sync_file "$OPENCLAW_REPO/memory/TASK-SYSTEM.md" "$CLAWD_DIR/memory/TASK-SYSTEM.md" "memory/TASK-SYSTEM.md" "template"
fi

# Sync skills
echo "📦 Checking skills..."
if [ "$TEMPLATES_ONLY" != true ]; then
    for skill in limitless fireflies quo; do
        sync_file "$OPENCLAW_REPO/skills/$skill/SKILL.md" "$CLAWD_DIR/skills/$skill/SKILL.md" "skills/$skill/SKILL.md" "skill"
        sync_file "$OPENCLAW_REPO/skills/$skill/$skill" "$CLAWD_DIR/skills/$skill/$skill" "skills/$skill/$skill" "skill"
        [ "$DRY_RUN" != true ] && chmod +x "$CLAWD_DIR/skills/$skill/$skill" 2>/dev/null || true
    done
    
    # Always update openclaw management skill
    sync_file "$OPENCLAW_REPO/skill/SKILL.md" "$CLAWD_DIR/skills/openclaw/SKILL.md" "skills/openclaw/SKILL.md" "skill"
    sync_file "$OPENCLAW_REPO/skill/openclaw" "$CLAWD_DIR/skills/openclaw/openclaw" "skills/openclaw/openclaw" "skill"
    [ "$DRY_RUN" != true ] && chmod +x "$CLAWD_DIR/skills/openclaw/openclaw" 2>/dev/null || true
fi

# Save checksums
if [ "$DRY_RUN" != true ]; then
    echo "$CHECKSUMS" > "$CHECKSUMS_FILE"
fi

echo ""

# Report conflicts
if [ -s "$CONFLICTS_LOG" ]; then
    echo "⚠️  Files with conflicts (your changes preserved):"
    cat "$CONFLICTS_LOG" | while read -r file; do
        echo "   - $file"
    done
    echo ""
    echo "To see upstream changes: openclaw diff"
    echo "To force update: openclaw sync --force"
else
    echo "✓ Sync complete!"
fi

echo ""
echo "Version: $NEW_VERSION"

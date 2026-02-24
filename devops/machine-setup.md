# OpenClaw Machine Setup

Desired state for every machine running an OpenClaw gateway. Each section describes
**what correct looks like**, how to **verify** it, and how to **fix** drift.

**How to use this document:**

1. Read each section's desired state
2. Check actual state using the verification commands
3. If actual matches desired: move on
4. If actual differs: apply the fix, then re-verify
5. Items marked **MANUAL** require human intervention (sudo, login, GUI) — flag these
   and stop

**See also:** `health-check.md` — ongoing monitoring agent that references this spec.

---

## Manual Prerequisites

These require human hands. An automated agent cannot complete them — flag any that are
missing and report to the admin.

### Tailscale

Every machine connects to the fleet via Tailscale. Without it, SSH and fleet management
don't work.

- Tailscale installed and running (requires admin privileges to install)
- Logged into the shared tailnet (requires browser authentication)
- Appears as `active` in `tailscale status`
- SSH enabled: `tailscale set --ssh`

**Verify:** `tailscale status --self | head -1` shows the machine with an active status.

### SSH

Remote Login must be enabled in System Settings > General > Sharing. This is a GUI
toggle — cannot be automated.

- SSH accessible over Tailscale IP
- Default sshd_config is fine — no tuning needed

**Verify from any fleet machine:** `ssh <tailscale-ip> "echo ok"`

### Homebrew

Package manager for macOS system tools. Requires admin privileges to install.

- Homebrew installed at `/opt/homebrew/` (Apple Silicon) or `/usr/local/` (Intel)

**Verify:** `brew --version`

### Firewall

If the macOS firewall is enabled, Tailscale and SSH must be allowed through.

**Verify:** `sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate`

---

## System

### Power Management

OpenClaw gateways must be always-reachable. Machines that sleep drop off the network and
miss messages.

| Setting        | Value | Why                                                      |
| -------------- | ----- | -------------------------------------------------------- |
| `sleep`        | `0`   | Never system sleep                                       |
| `displaysleep` | `10`  | Display can sleep (saves energy, doesn't affect network) |
| `womp`         | `1`   | Wake on LAN                                              |
| `tcpkeepalive` | `1`   | Keep network connections alive during display sleep      |
| `powernap`     | `1`   | Background tasks during display sleep                    |
| `autorestart`  | `1`   | Auto-restart after power failure                         |

**Verify:**
`pmset -g | grep -E 'sleep |displaysleep|womp|tcpkeepalive|powernap|autorestart'`

**Fix (MANUAL — requires sudo):**

```bash
sudo pmset -a sleep 0
sudo pmset -a displaysleep 10
sudo pmset -a womp 1
sudo pmset -a tcpkeepalive 1
sudo pmset -a powernap 1
sudo pmset -a autorestart 1
```

### Permissions

The OpenClaw config directory contains API keys and tokens. It must not be
world-readable.

- `~/.openclaw` directory permissions: `700`

**Verify:** `stat -f '%Lp' ~/.openclaw` returns `700`

**Fix:** `chmod 700 ~/.openclaw`

---

## Software

Install everything via Homebrew where possible. No version pins — always use latest
stable. The goal is consistency across machines, not a specific version.

### Node.js

The gateway runs on Node.js. Install via nvm for version management.

- nvm installed
- Current LTS or latest stable Node.js installed
- `node` and `npm` available in PATH

**Verify:** `node --version && npm --version`

**Fix:**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install node
```

### OpenClaw

The gateway binary. Install globally via npm.

- `openclaw` available in PATH
- Running the latest stable release

**Verify:** `which openclaw && openclaw --version`

**Fix:** `npm install -g openclaw@latest`

### pnpm

Required for OpenClaw skill installation. Install globally via npm.

- `pnpm` available in PATH

**Verify:** `pnpm --version`

**Fix:** `npm install -g pnpm`

### uv

Python package runner for standalone skills (Python-based CLIs with inline
dependencies). Install via Homebrew.

- `uv` available in PATH via Homebrew (not the standalone installer)

**Verify:** `which uv && uv --version` — path should be under Homebrew, not
`~/.local/bin`

**Fix:** `brew install uv`

### restic

Backup tool for workspace protection. Install via Homebrew.

- `restic` available in PATH via Homebrew

**Verify:** `which restic && restic version`

**Fix:** `brew install restic`

### Claude CLI

Used by the health check agent and for fleet operations. Installed via Anthropic's
official installer (lands in `~/.local/bin/`).

- `claude` available in PATH
- Must work over non-interactive SSH, not just local terminal

**Verify:** `claude --version` — must also work via `ssh <host> "claude --version"`

**Fix:** `npm install -g @anthropic-ai/claude-code`

---

## Shell Environment

Software installed to `~/.local/bin` (Claude CLI) and `/opt/homebrew/bin` (Homebrew
packages) must be available to **non-interactive** shells — SSH commands and cron jobs,
not just interactive terminals.

The following paths must be in PATH for all shell contexts:

- `~/.local/bin` (Claude CLI, any pip/uv installed tools)
- `/opt/homebrew/bin` (Homebrew packages: restic, uv, etc.)
- nvm's Node.js bin directory

**How this is configured depends on the shell.** The important thing is that
`ssh <host> "node --version && uv --version && claude --version"` all work — not just in
a local terminal.

**Verify:**
`ssh <tailscale-ip> 'echo node: $(node --version) && echo uv: $(uv --version) && echo claude: $(claude --version)'`
— all three must resolve. (Single quotes required — double quotes expand substitutions
locally before SSH.)

---

## Gateway

The OpenClaw gateway runs as a launchd user agent that auto-starts on login.

- launchd label: `ai.openclaw.gateway`
- Binding: loopback (localhost only — Tailscale handles remote access)
- Must have a running PID

**Verify:** `launchctl list | grep ai.openclaw.gateway` — should show a PID in the first
column (not `-`)

**Health:** `openclaw health` — should report gateway up, channels connected

---

## Backup

Restic backs up all of `~/.openclaw/` to a local repository. This protects against bad
updates, accidental overwrites, and AI-mangled memory files.

### Repository

- Location: `~/openclaw-backups`
- Password file: `~/.openclaw/restic-password` (permissions `600`)
- Password: `openclaw-local-backup`
- Excludes: `browser/`, `skill-venv/`, `logs/` (all regenerable)

**Verify repo exists:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups snapshots | tail -3`

**Fix (initialize new repo):**

```bash
echo "openclaw-local-backup" > ~/.openclaw/restic-password
chmod 600 ~/.openclaw/restic-password
RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic init --repo ~/openclaw-backups
```

### Automated Schedule

Two launchd agents handle backup automation:

| Agent  | Label                          | Schedule             | Purpose                         |
| ------ | ------------------------------ | -------------------- | ------------------------------- |
| Backup | `ai.openclaw.workspace-backup` | Every 4 hours        | Incremental backup + prune      |
| Verify | `ai.openclaw.backup-verify`    | Weekly (Sunday 4 AM) | Integrity check (10% data read) |

Plist files are in `~/.openclaw-config/devops/`:

- `ai.openclaw.workspace-backup.plist`
- `ai.openclaw.backup-verify.plist`

**Fix (deploy schedule):**

```bash
cp ~/.openclaw-config/devops/ai.openclaw.workspace-backup.plist ~/Library/LaunchAgents/
cp ~/.openclaw-config/devops/ai.openclaw.backup-verify.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.openclaw.workspace-backup.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.backup-verify.plist
```

### Retention Policy

- Keep 7 daily snapshots
- Keep 4 weekly snapshots
- Keep 6 monthly snapshots

**Verify services running:**

- `launchctl list | grep ai.openclaw.workspace-backup` (shows PID)
- `launchctl list | grep ai.openclaw.backup-verify` (loaded, may show `-` PID between
  runs)

**Verify backup freshness:** Most recent snapshot should be within the last 8 hours.

### Manual Operations

**Run a backup now:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups backup ~/.openclaw --exclude browser --exclude skill-venv --exclude logs`

**Restore a file:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups restore latest --target /tmp/restore --include "MEMORY.md"`

**List snapshots:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups snapshots`

**Verify integrity:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups check --read-data-subset=10%`

---

## Agent Defaults

These settings go in `~/.openclaw/openclaw.json` under `agents.defaults`. They define
shared behavior for every OpenClaw instance — not model choices or API keys (those are
user-specific).

**`USE_MID_TIER_MODEL` is a placeholder** — replace it with the actual mid-tier model ID
for this machine's provider (e.g. `anthropic/claude-sonnet-4-6` for Anthropic,
`openrouter/anthropic/claude-sonnet-4.6` for OpenRouter). The point is: don't burn the
primary (opus-class) model on hourly pings and background work.

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "24h"
      },
      "compaction": {
        "mode": "safeguard"
      },
      "thinkingDefault": "high",
      "typingMode": "message",
      "heartbeat": {
        "every": "1h",
        "model": "USE_MID_TIER_MODEL"
      },
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8,
        "model": "USE_MID_TIER_MODEL",
        "thinking": "medium"
      }
    }
  }
}
```

**Notes:**

- `contextPruning: cache-ttl / 24h` — prune conversation context older than 24 hours
- `compaction: safeguard` — safe compaction when approaching context limits
- `thinkingDefault: high` — agents think deeply by default
- `typingMode: message` — deliver full messages rather than streaming partial text
- `maxConcurrent: 4` — max simultaneous conversations
- `subagents.maxConcurrent: 8` — max parallel subagent calls

**Verify:** Read `~/.openclaw/openclaw.json` and confirm each key is present with the
expected value. Missing keys mean the default (often unset) applies, which may not match
baseline.

---

## Message Handling

These settings go in `~/.openclaw/openclaw.json` under `messages`.

```json
{
  "messages": {
    "queue": {
      "mode": "steer"
    },
    "ackReaction": "👀",
    "ackReactionScope": "all",
    "removeAckAfterReply": true
  }
}
```

- `queue.mode: steer` — new messages from the user steer the running conversation
  mid-response, rather than queuing for sequential processing
- `ackReaction: 👀` — immediately react to every incoming message with eyes, so the user
  knows the agent received it
- `ackReactionScope: all` — react to all messages, not just direct mentions
- `removeAckAfterReply: true` — remove the 👀 reaction once the agent responds (clean
  UX)

**Verify:** Check `messages` section in `~/.openclaw/openclaw.json`.

---

## Workspace

### Core Files

Every workspace at `~/.openclaw/workspace/` must contain these files:

| File           | Purpose                                             |
| -------------- | --------------------------------------------------- |
| `AGENTS.md`    | Operating instructions                              |
| `SOUL.md`      | Personality definition                              |
| `USER.md`      | Human profile                                       |
| `MEMORY.md`    | Always-loaded context                               |
| `IDENTITY.md`  | Quick reference card (must be under 305 characters) |
| `HEARTBEAT.md` | Periodic check config                               |
| `TOOLS.md`     | Local environment notes                             |
| `BOOT.md`      | Startup routine                                     |

**Verify:**
`ls ~/.openclaw/workspace/{AGENTS,SOUL,USER,MEMORY,IDENTITY,HEARTBEAT,TOOLS,BOOT}.md`

### Memory Structure

```
~/.openclaw/workspace/memory/
├── daily/
├── decisions/
├── imports/
├── people/
├── projects/
└── topics/
```

**Verify:**
`ls -d ~/.openclaw/workspace/memory/{daily,decisions,imports,people,projects,topics}`

### Config Repo

Each machine should have the openclaw-config repository cloned locally for updates and
health check reference.

- Location: `~/.openclaw-config`
- Remote: the upstream openclaw-config repository
- Should be on the default branch and up to date

**Verify:** `test -f ~/.openclaw-config/VERSION && git -C ~/.openclaw-config status`

**Fix:**
`git clone https://github.com/TechNickAI/openclaw-config.git ~/.openclaw-config`

---

## Health Check Admin

The health check agent needs to know where to send system alerts. This is stored in a
simple two-line file at `~/.openclaw/health-check-admin`:

```
<admin-name>
openclaw message send --channel telegram --target "<admin-telegram-id>" --message "{MESSAGE}"
```

- Line 1: Admin's name (for prompt context)
- Line 2: Command template with `{MESSAGE}` placeholder
- The health check agent reads this file and uses it to notify the fleet admin
- This is for **system health alerts only** — not user-facing cron outputs

**Verify:** `cat ~/.openclaw/health-check-admin` — should have exactly 2 lines: a real
name and a send command with a real Telegram ID. `<admin-name>` and
`<admin-telegram-id>` are placeholders — they must be replaced with actual values.

---

## Hooks

These internal hooks should be enabled in `~/.openclaw/openclaw.json` under `hooks`:

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "boot-md": {
          "enabled": true
        },
        "command-logger": {
          "enabled": true
        },
        "session-memory": {
          "enabled": true
        }
      }
    }
  }
}
```

| Hook             | Purpose                                                             |
| ---------------- | ------------------------------------------------------------------- |
| `boot-md`        | Runs BOOT.md on agent startup — establishes context and orientation |
| `command-logger` | Logs all commands executed — audit trail                            |
| `session-memory` | Tracks session state in memory — continuity across conversations    |

**Verify:** Check `hooks.internal.entries` in `~/.openclaw/openclaw.json` — all three
should be present and enabled.

---

## Verification

Run these checks to confirm a machine meets this spec. Every check should pass. Any
failure means the machine has drifted from desired state.

### Quick Compliance (single command)

```bash
echo "=== system ===" && \
echo "sleep: $(pmset -g | grep ' sleep ' | awk '{print $2}')" && \
echo "displaysleep: $(pmset -g | grep displaysleep | awk '{print $2}')" && \
echo "womp: $(pmset -g | grep ' womp ' | awk '{print $2}')" && \
echo "tcpkeepalive: $(pmset -g | grep tcpkeepalive | awk '{print $2}')" && \
echo "powernap: $(pmset -g | grep powernap | awk '{print $2}')" && \
echo "autorestart: $(pmset -g | grep autorestart | awk '{print $2}')" && \
echo "permissions: $(stat -f '%Lp' ~/.openclaw)" && \
echo "=== network ===" && \
echo "tailscale: $(tailscale status --self 2>/dev/null | head -1 || echo 'NOT RUNNING')" && \
echo "=== software ===" && \
echo "node: $(node --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "openclaw: $(openclaw --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "pnpm: $(pnpm --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "uv: $(uv --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "restic: $(restic version 2>/dev/null || echo 'NOT FOUND')" && \
echo "claude: $(claude --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "=== services ===" && \
GW_PID=$(launchctl list 2>/dev/null | grep ai.openclaw.gateway | awk '{print $1}') && \
{ [[ "$GW_PID" =~ ^[0-9]+$ ]] && echo "gateway: running (PID $GW_PID)" || echo "gateway: NOT RUNNING"; } && \
echo "backup: $(launchctl list 2>/dev/null | grep -q ai.openclaw.workspace-backup && echo 'loaded' || echo 'NOT LOADED')" && \
echo "backup-verify: $(launchctl list 2>/dev/null | grep -q ai.openclaw.backup-verify && echo 'loaded' || echo 'NOT LOADED')" && \
echo "backup-freshness: $(RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups snapshots --latest 1 --json 2>/dev/null | python3 -c "import sys,json; s=json.load(sys.stdin); print(s[0]['time'][:19] if s else 'NO SNAPSHOTS')" 2>/dev/null || echo 'NO REPO')" && \
echo "=== workspace ===" && \
ls ~/.openclaw/workspace/{AGENTS,SOUL,USER,MEMORY,IDENTITY,HEARTBEAT,TOOLS,BOOT}.md >/dev/null 2>&1 && echo "core files: all present" || echo "core files: MISSING" && \
ls -d ~/.openclaw/workspace/memory/{daily,decisions,imports,people,projects,topics} >/dev/null 2>&1 && echo "memory dirs: all present" || echo "memory dirs: MISSING" && \
echo "config-repo: $(test -f ~/.openclaw-config/VERSION && echo 'present' || echo 'MISSING')" && \
echo "health-check-admin: $(test -f ~/.openclaw/health-check-admin && echo 'present' || echo 'MISSING')"
```

### Expected Results

```
=== system ===
sleep: 0
displaysleep: 10
womp: 1
tcpkeepalive: 1
powernap: 1
autorestart: 1
permissions: 700
=== network ===
tailscale: <ip>  <hostname>  <user>@  macOS  -
=== software ===
node: v<version>
openclaw: <version>
pnpm: <version>
uv: uv <version>
restic: restic <version>
claude: <version> (Claude Code)
=== services ===
gateway: running (PID <number>)
backup: loaded
backup-verify: loaded
backup-freshness: <ISO timestamp within last 8 hours>
=== workspace ===
core files: all present
memory dirs: all present
config-repo: present
health-check-admin: present
```

Any line showing `NOT FOUND`, `NOT RUNNING`, `NOT LOADED`, or `MISSING` indicates drift
that needs to be resolved.

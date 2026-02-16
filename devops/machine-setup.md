# OpenClaw Host Machine Setup

Baseline configuration for every machine running an OpenClaw gateway. The health check
agent can verify these settings; fleet management uses this as the source of truth for
what "correctly configured" means.

## Power Management

OpenClaw gateways must be always-reachable. Machines that sleep drop off Tailscale and
miss messages.

```bash
sudo pmset -a sleep 0           # Never system sleep
sudo pmset -a displaysleep 10   # Display can sleep (saves energy, doesn't affect network)
sudo pmset -a womp 1            # Wake on LAN
sudo pmset -a tcpkeepalive 1    # Keep network connections alive during display sleep
sudo pmset -a powernap 1        # Background tasks during display sleep
sudo pmset -a autorestart 1     # Auto-restart after power failure
```

**Verify:**
`pmset -g | grep -E 'sleep |displaysleep|womp|tcpkeepalive|powernap|autorestart'`

**Expected:**

```
sleep            0
displaysleep     10
womp             1
tcpkeepalive     1
powernap         1
autorestart      1
```

## Network — Tailscale

Every machine connects to the fleet via Tailscale. Without it, SSH and fleet management
don't work.

- Tailscale installed and running
- Logged into the shared tailnet
- Appears as `active` in `tailscale status`
- SSH enabled: `tailscale set --ssh` (allows Tailscale-authenticated SSH)

**Verify:** `tailscale status | head -5`

## Network — SSH

Remote Login must be enabled in System Settings > General > Sharing.

- `/etc/ssh/sshd_config` can be default — no special tuning needed
- SSH must be accessible over Tailscale IP

**Verify from master:** `ssh <alias> "echo ok"`

## Network — Firewall

If the macOS firewall is enabled, Tailscale and SSH must be allowed through.

**Verify:** `sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate`

## Permissions

The OpenClaw config directory contains API keys and tokens. It must not be
world-readable.

```bash
chmod 700 ~/.openclaw
```

**Verify:** `stat -f '%Lp' ~/.openclaw` should return `700`

## Software

### Node.js

The gateway runs on Node.js. Install via nvm for consistent version management.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 24
```

**Verify:** `node --version` (should be v24+)

### OpenClaw

```bash
npm install -g openclaw@latest
```

**Verify:** `which openclaw && openclaw --version`

### Claude CLI

Used by the health check agent and for fleet operations. Installed via Anthropic's
installer, lands in `~/.local/bin/`.

**Important:** `~/.local/bin` must be in PATH for both interactive and non-interactive
shells. Add to `~/.zshenv` (not `.zshrc`) so SSH sessions pick it up:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshenv
```

Using `.zshenv` instead of `.zshrc` ensures the PATH is set for non-interactive SSH
commands (like `ssh host "claude --version"`), not just interactive terminal sessions.

**Verify:** `ssh <alias> "claude --version"` (must work over SSH, not just locally)

## Services

### Gateway (required)

The OpenClaw gateway runs as a launchd user agent that auto-starts on login.

**Verify:** `launchctl list | grep ai.openclaw.gateway` (should show a PID)

### Workspace Backup (required)

Restic backs up all of `~/.openclaw/` to a local repository. This protects against bad
updates, accidental overwrites, and AI-mangled memory files — not just machine failure.

Excludes `browser/`, `skill-venv/`, and `logs/` (all regenerable and large).

**Install:**

```bash
brew install restic
```

**Initialize:**

```bash
echo "openclaw-local-backup" > ~/.openclaw/restic-password
chmod 600 ~/.openclaw/restic-password
RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic init --repo ~/openclaw-backups
```

**Automated schedule:** Runs every 4 hours via launchd, keeps 7 daily + 4 weekly + 6
monthly snapshots. Weekly verification checks repository integrity and alerts on
failure.

```bash
cp <openclaw-config>/devops/ai.openclaw.workspace-backup.plist ~/Library/LaunchAgents/
cp <openclaw-config>/devops/ai.openclaw.backup-verify.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.openclaw.workspace-backup.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.backup-verify.plist
```

**Manual backup:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups backup ~/.openclaw --exclude browser --exclude skill-venv --exclude logs`

**Restore a file:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups restore latest --target /tmp/restore --include "MEMORY.md"`

**List snapshots:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups snapshots`

**Verify integrity:**
`RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups check --read-data-subset=10%`

**Verify services:**

- `launchctl list | grep ai.openclaw.workspace-backup` (backup agent running)
- `launchctl list | grep ai.openclaw.backup-verify` (weekly verification running)
- Snapshots:
  `RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups snapshots | tail -3`

## OpenClaw Configuration

### Workspace

Core files in `~/.openclaw/workspace/`:

| File           | Purpose                 |
| -------------- | ----------------------- |
| `AGENTS.md`    | Operating instructions  |
| `SOUL.md`      | Personality definition  |
| `USER.md`      | Human profile           |
| `MEMORY.md`    | Always-loaded context   |
| `IDENTITY.md`  | Quick reference card    |
| `HEARTBEAT.md` | Periodic check config   |
| `TOOLS.md`     | Local environment notes |

**Verify:**
`ls ~/.openclaw/workspace/{AGENTS,SOUL,USER,MEMORY,IDENTITY,HEARTBEAT,TOOLS}.md`

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

### Embeddings

Every machine needs vector embeddings for semantic memory search.

- **Master:** Local LM Studio at `127.0.0.1:1234`
- **Fleet machines:** Remote LM Studio at master's Tailscale IP `:1234`
- **Fallback:** OpenAI API (all machines need an API key)
- **Model:** `text-embedding-embeddinggemma-300m-qat`

Configured in `~/.openclaw/openclaw.json` under `memory.search`.

### Config Repo

Each machine should have openclaw-config cloned for updates:

```bash
git clone https://github.com/TechNickAI/openclaw-config.git ~/.openclaw-config
```

**Verify:** `ls ~/.openclaw-config/VERSION`

## Quick Compliance Check

One-liner to check the critical settings (run via SSH from master):

```bash
ssh <alias> "echo 'sleep:' && pmset -g | grep ' sleep ' | awk '{print \$2}' && \
echo 'autorestart:' && pmset -g | grep autorestart | awk '{print \$2}' && \
echo 'permissions:' && stat -f '%Lp' ~/.openclaw && \
echo 'gateway:' && (launchctl list | grep -q ai.openclaw.gateway && echo 'running' || echo 'NOT RUNNING') && \
echo 'claude:' && (~/.local/bin/claude --version 2>/dev/null || echo 'NOT FOUND') && \
echo 'tailscale:' && (tailscale status --self 2>/dev/null | head -1 || echo 'NOT RUNNING')"
```

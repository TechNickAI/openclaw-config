# OpenClaw Machine Setup — Linux

Linux-specific setup for OpenClaw gateway machines. Read alongside `machine-setup.md`
(Mac/shared concepts).

**How to use this document:**

1. Read each section's desired state
2. Check actual state using the verification commands
3. If actual matches desired: move on
4. If actual differs: apply the fix, then re-verify
5. Items marked **MANUAL** require human intervention — flag these and stop

---

## Manual Prerequisites

### Tailscale

Every machine connects to the fleet via Tailscale.

- Tailscale installed and running
- Logged into the shared tailnet
- Appears as `active` in `tailscale status`

**Install (MANUAL — requires sudo):**

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**Verify:** `tailscale status --self | head -1`

### SSH

EC2 instances have SSH enabled by default. Ensure the fleet SSH key (`~/.ssh/id_ed25519`
on nicks-macly) is in `~/.ssh/authorized_keys`.

**Verify from master:** `ssh <hostname> "echo ok"`

---

## System

### Power Management

EC2 instances are always-on — no sleep settings needed. Skip the `pmset` section from
`machine-setup.md` entirely.

**Verify:** The instance is reachable. That's it.

### Permissions

```bash
chmod 700 ~/.openclaw
```

**Verify:** `stat -c '%a' ~/.openclaw` returns `700`

---

## Software

### System Packages

System tools via `apt`. See `devops/apt-packages.txt` for the full list.

**Verify:** `sudo apt list --installed 2>/dev/null | grep -E 'jq|restic|tmux'`

**Fix:**

```bash
sudo apt update
sudo apt install -y $(grep -v '^#' ~/src/openclaw-config/devops/apt-packages.txt | tr '\n' ' ')
```

### Parallel CLI

The Parallel.ai CLI provides web search, content extraction, deep research, and data
enrichment. Used by the `parallel` skill. Not available via apt — use the official
installer.

- `parallel-cli` binary in PATH (installed to `~/.local/bin`)

**Verify:** `parallel-cli --version`

**Fix:**

```bash
curl -fsSL https://parallel.ai/install.sh | bash
```

Installs to `~/.local/bin` (already in PATH on fleet machines). The `parallel` skill
auto-installs this on first use if missing.

### Node.js

Ubuntu ships with a recent Node.js via apt. No nvm needed on server machines.

- Node.js installed via apt (Ubuntu 24.04 includes Node 18+; use NodeSource PPA for Node
  22+)
- `node` and `npm` available in PATH
- npm global prefix set to `~/.npm-global` (avoids sudo for global installs)

**Verify:** `node --version && npm --version`

**Fix (NodeSource PPA for Node 22+):**

```bash
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### npm Global Packages

- `openclaw` — the gateway binary (latest stable)
- `pnpm` — required for skill installation
- `@anthropic-ai/claude-code` — Claude CLI for health checks and fleet ops

**Verify:**

```bash
openclaw --version && pnpm --version && claude --version
```

**Fix:**

```bash
npm install -g openclaw@latest pnpm @anthropic-ai/claude-code
```

---

## Shell Environment

All installed tools must be in PATH for **non-interactive** shells — SSH commands and
systemd services, not just interactive terminals.

These paths must be in PATH for all shell contexts:

- `~/.npm-global/bin` — openclaw, pnpm, claude
- `~/.local/bin` — uv and other user-installed tools

**Configure in `~/.zshrc` (or `~/.bashrc`):**

```bash
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
```

**Verify (non-interactive):**

```bash
ssh <hostname> 'echo node: $(node --version) && echo uv: $(uv --version) && echo claude: $(~/.npm-global/bin/claude --version)'
```

Note: systemd service files explicitly set `PATH=` — see `devops/linux/` unit files.

---

## Gateway

The OpenClaw gateway runs as a **systemd user** service.

- Service name: `openclaw-gateway.service`
- Binding: loopback (localhost only — Tailscale handles remote access)
- Auto-starts on login via `WantedBy=default.target`

**Install gateway:**

```bash
npm install -g openclaw@latest
openclaw gateway setup   # generates and enables the systemd unit
```

**Verify:** `systemctl --user status openclaw-gateway` — should show `active (running)`

**Restart:** `systemctl --user restart openclaw-gateway`

**Logs:** `journalctl --user -u openclaw-gateway -f`

---

## Backup

Restic backs up all of `~/.openclaw/` to a local repository.

### Repository

- Location: `~/openclaw-backups`
- Password file: `~/.openclaw/restic-password` (permissions `600`)
- Password: `openclaw-local-backup`
- Excludes: `browser/`, `skill-venv/`, `logs/` (all regenerable)

**Verify repo exists:**

```bash
RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups snapshots | tail -3
```

**Fix (initialize new repo):**

```bash
echo "openclaw-local-backup" > ~/.openclaw/restic-password
chmod 600 ~/.openclaw/restic-password
RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic init --repo ~/openclaw-backups
```

### Automated Schedule (systemd timers)

Two systemd timer pairs handle backup automation:

| Timer                             | Schedule             | Purpose                         |
| --------------------------------- | -------------------- | ------------------------------- |
| `openclaw-workspace-backup.timer` | Every 4 hours        | Incremental backup + prune      |
| `openclaw-backup-verify.timer`    | Weekly (Sunday 4 AM) | Integrity check (10% data read) |

Unit files are in `~/src/openclaw-config/devops/linux/`.

**Deploy:**

```bash
cp ~/src/openclaw-config/devops/linux/openclaw-workspace-backup.* ~/.config/systemd/user/
cp ~/src/openclaw-config/devops/linux/openclaw-backup-verify.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now openclaw-workspace-backup.timer
systemctl --user enable --now openclaw-backup-verify.timer
```

**Verify:**

```bash
systemctl --user list-timers | grep openclaw
```

### Retention Policy

- Keep 7 daily snapshots
- Keep 4 weekly snapshots
- Keep 6 monthly snapshots

---

## Health Check

The health check runs every 30 minutes via systemd timer and invokes Claude Code with
`devops/health-check.md` as the prompt.

Unit files: `~/src/openclaw-config/devops/linux/openclaw-health-check.*`

**Deploy:**

```bash
cp ~/src/openclaw-config/devops/linux/openclaw-health-check.* ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now openclaw-health-check.timer
```

**Verify:**

```bash
systemctl --user list-timers | grep health-check
```

**Logs:** `~/.openclaw/health-check-cron.log`

### health-check-admin file

Create `~/.openclaw/health-check-admin` with two lines — admin name and Telegram
notification command:

```
Nick
openclaw message send --channel telegram --target "<NICK_TELEGRAM_ID>" --message "{MESSAGE}"
```

**Verify:** `cat ~/.openclaw/health-check-admin` — should have 2 non-placeholder lines.

---

## Workspace

### Core Files

Every workspace at the configured workspace path must contain:

| File           | Purpose                 |
| -------------- | ----------------------- |
| `AGENTS.md`    | Operating instructions  |
| `SOUL.md`      | Personality definition  |
| `USER.md`      | Human profile           |
| `MEMORY.md`    | Always-loaded context   |
| `IDENTITY.md`  | Quick reference card    |
| `HEARTBEAT.md` | Periodic check config   |
| `TOOLS.md`     | Local environment notes |
| `BOOT.md`      | Startup routine         |

**Verify:** `ls <workspace>/{AGENTS,SOUL,USER,MEMORY,IDENTITY,HEARTBEAT,TOOLS,BOOT}.md`

### Memory Structure

```
<workspace>/memory/
├── people/
├── projects/
├── decisions/
└── topics/
```

### Workspace Path

Configure `agents.defaults.workspace` in `~/.openclaw/openclaw.json` as
`~/.openclaw/workspace`. This keeps the workspace inside the directory the backup
service already covers. If the workspace lives elsewhere (e.g. `~/openclaw/workspace` —
the wizard default), the backup service will detect and include it, but the preferred
layout is inside `~/.openclaw/`.

### Config Repo

- Location: `~/src/openclaw-config`
- Remote: the upstream openclaw-config repository

**Verify:**
`test -f ~/src/openclaw-config/VERSION && git -C ~/src/openclaw-config status`

**Fix:**
`git clone https://github.com/TechNickAI/openclaw-config.git ~/src/openclaw-config`

---

## Verification

### Quick Compliance (Linux)

```bash
echo "=== system ===" && \
echo "permissions: $(stat -c '%a' ~/.openclaw)" && \
echo "=== network ===" && \
echo "tailscale: $(tailscale status --self 2>/dev/null | head -1 || echo 'NOT RUNNING')" && \
echo "=== software ===" && \
echo "restic: $(dpkg -l restic 2>/dev/null | grep ^ii | awk '{print $3}' || echo 'NOT INSTALLED')" && \
echo "node: $(node --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "openclaw: $(openclaw --version 2>/dev/null || ~/.npm-global/bin/openclaw --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "pnpm: $(pnpm --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "claude: $(claude --version 2>/dev/null || ~/.npm-global/bin/claude --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "parallel-cli: $(parallel-cli --version 2>/dev/null || ~/.local/bin/parallel-cli --version 2>/dev/null || echo 'NOT FOUND')" && \
echo "=== services ===" && \
echo "gateway: $(systemctl --user is-active openclaw-gateway 2>/dev/null || echo 'unknown')" && \
echo "backup-timer: $(systemctl --user is-active openclaw-workspace-backup.timer 2>/dev/null || echo 'NOT ACTIVE')" && \
echo "health-timer: $(systemctl --user is-active openclaw-health-check.timer 2>/dev/null || echo 'NOT ACTIVE')" && \
echo "backup-freshness: $(RESTIC_PASSWORD_FILE=~/.openclaw/restic-password restic -r ~/openclaw-backups snapshots --latest 1 --json 2>/dev/null | python3 -c "import sys,json; s=json.load(sys.stdin); print(s[0]['time'][:19] if s else 'NO SNAPSHOTS')" 2>/dev/null || echo 'NO REPO')" && \
echo "=== workspace ===" && \
WORKSPACE=$(python3 -c "import json; d=json.load(open(\"$HOME/.openclaw/openclaw.json\")); print(d['agents']['defaults'].get('workspace','NOT SET'))") && \
ls "$WORKSPACE"/{AGENTS,SOUL,USER,MEMORY,IDENTITY,HEARTBEAT,TOOLS,BOOT}.md >/dev/null 2>&1 && echo "core files: all present" || echo "core files: MISSING" && \
echo "config-repo: $(test -f ~/src/openclaw-config/VERSION && echo 'present' || echo 'MISSING')" && \
echo "health-check-admin: $(test -f ~/.openclaw/health-check-admin && echo 'present' || echo 'MISSING')"
```

### Expected Results

```
=== system ===
permissions: 700
=== network ===
tailscale: <ip>  <hostname>  <user>@  linux  -
=== software ===
restic: <version>
node: v<version>
openclaw: <version>
pnpm: <version>
claude: <version> (Claude Code)
parallel-cli: <version>
=== services ===
gateway: active
backup-timer: active
health-timer: active
backup-freshness: <ISO timestamp within last 8 hours>
=== workspace ===
core files: all present
config-repo: present
health-check-admin: present
```

Any line showing `NOT FOUND`, `NOT ACTIVE`, or `MISSING` indicates drift.

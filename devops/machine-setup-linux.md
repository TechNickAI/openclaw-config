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

## Instance Sizing

EC2 instances need enough RAM for the OpenClaw gateway, whisper.cpp transcription, and
compilation of native packages. `t4g.small` (2GB) is insufficient — compilation OOMs and
whisper can't run alongside the gateway.

- **Minimum:** `t4g.medium` (2 vCPU, 4GB RAM)
- **Storage:** 30GB gp3 root volume

**Verify:** `free -h | head -2` — should show ~3.7Gi total

### Swap

All machines should have a 2GB swapfile as safety margin for memory spikes during
compilation and transcription.

**Verify:** `swapon --show`

**Fix:**

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

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

### Homebrew (Linuxbrew)

Homebrew on Linux for packages not available via apt.

- Binary: `/home/linuxbrew/.linuxbrew/bin/brew`
- Over SSH (non-login shell), use the full path

**Verify:** `/home/linuxbrew/.linuxbrew/bin/brew --version`

**Fix:**

```bash
NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
```

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
- `@anthropic-ai/claude-code` — Claude CLI for health checks and fleet ops

**Verify:**

```bash
openclaw --version && claude --version
```

**Fix:**

```bash
npm install -g openclaw@latest @anthropic-ai/claude-code
```

### pnpm

Standalone pnpm install (preferred over `npm install -g pnpm` — avoids npm global prefix
issues). Installs to `~/.local/share/pnpm`.

**Verify:** `pnpm --version` (or `~/.local/share/pnpm/pnpm --version` over SSH)

**Fix:**

```bash
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

---

## Shell Environment

All installed tools must be in PATH for **non-interactive** shells — SSH commands and
systemd services, not just interactive terminals.

These paths must be in PATH for all shell contexts:

- `~/.npm-global/bin` — openclaw, claude
- `~/.local/bin` — uv and other user-installed tools
- `~/.local/share/pnpm` — pnpm (standalone installer)
- `/home/linuxbrew/.linuxbrew/bin` — Homebrew packages

**Configure in `~/.zshrc` (or `~/.bashrc`):**

```bash
export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$HOME/.local/share/pnpm:$PATH"
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
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

## Voice Transcription (whisper.cpp)

Local speech-to-text using whisper.cpp — compiled from source for ARM64 (Graviton). Used
by the Contact Steward workflow to transcribe voice messages.

- Binary: `/usr/local/bin/whisper-cli`
- Server: `/usr/local/bin/whisper-server`
- Model: `/opt/whisper.cpp/models/ggml-small.bin` (~466MB)
- Source: `/opt/whisper.cpp/`

The `small` model is the sweet spot for t4g.medium — `base` is less accurate on accented
speech, `medium` (~1.5GB) uses too much RAM alongside the gateway.

**Verify:**
`whisper-cli -m /opt/whisper.cpp/models/ggml-small.bin -f /opt/whisper.cpp/samples/jfk.wav -np -nt`

**Fix:**

```bash
# Requires build-essential and cmake (see apt-packages.txt)
sudo git clone https://github.com/ggerganov/whisper.cpp.git /opt/whisper.cpp
cd /opt/whisper.cpp

# Build with -j1 on 4GB machines to avoid OOM (-j2 is fine with 8GB+)
sudo cmake -B build -DWHISPER_BUILD_TESTS=OFF -DWHISPER_BUILD_EXAMPLES=ON
sudo cmake --build build --config Release -j1

# Download small model
sudo bash models/download-ggml-model.sh small

# Symlink to PATH
sudo ln -sf /opt/whisper.cpp/build/bin/whisper-cli /usr/local/bin/whisper-cli
sudo ln -sf /opt/whisper.cpp/build/bin/whisper-server /usr/local/bin/whisper-server
```

**Usage:**

```bash
# Transcribe a file (supports flac, mp3, ogg, wav)
whisper-cli -m /opt/whisper.cpp/models/ggml-small.bin -f audio.wav -np -nt

# JSON output
whisper-cli -m /opt/whisper.cpp/models/ggml-small.bin -f audio.wav -oj -of result
```

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
echo "ram: $(free -h | awk '/Mem:/{print $2}')" && \
echo "swap: $(swapon --show --noheadings | awk '{print $3}' || echo 'NONE')" && \
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
echo "brew: $(/home/linuxbrew/.linuxbrew/bin/brew --version 2>/dev/null | head -1 || echo 'NOT FOUND')" && \
echo "whisper: $(whisper-cli -h 2>/dev/null | head -1 && echo 'installed' || echo 'NOT FOUND')" && \
echo "whisper-model: $(test -f /opt/whisper.cpp/models/ggml-small.bin && echo 'small model present' || echo 'MISSING')" && \
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
ram: 3.7Gi (or more)
swap: 2G
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
brew: Homebrew <version>
whisper: installed
whisper-model: small model present
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

# Remote Desktop Setup — Linux

VNC-based remote desktop for fleet Linux servers. Provides a lightweight graphical
desktop (Xfce4) with Chromium browser, accessible via VNC client from macOS.

Two modes:

- **Always-on** — for servers that need persistent screen sharing (e.g. hex)
- **On-demand** — start/stop as needed for debugging or browser tasks

---

## Packages

Required apt packages for VNC + desktop:

```
xfce4-session
xfce4-terminal
xfce4-panel
thunar
dbus-x11
tigervnc-standalone-server
```

These are not in `apt-packages.txt` because not every fleet machine needs a desktop.
Install manually on machines that need it.

**Note:** Install individual xfce4 packages rather than the `xfce4` metapackage to avoid
pulling in unnecessary dependencies. `thunar` is required for desktop icon launching
(without it, double-clicking `.desktop` files fails with "requires a file manager
service").

**Install desktop + VNC:**

```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y \
  xfce4-session xfce4-terminal xfce4-panel thunar dbus-x11 \
  tigervnc-standalone-server
```

**Verify:**

```bash
dpkg -s xfce4-session tigervnc-standalone-server thunar 2>&1 | grep -E '^Package:|^Status:'
```

Each package should show `Status: install ok installed`.

### Browser (Chromium via Playwright)

On Ubuntu 24.04 ARM64, `chromium-browser` is a snap transitional package that is
unreliable in VNC sessions. Use Playwright's Chromium instead — it bundles a real
Chromium binary with no snap dependency.

**Install system dependencies first (requires sudo), then browser binary as user:**

```bash
sudo npx playwright install --with-deps chromium
npx playwright install chromium
```

The `sudo` run installs ~30 system libraries (libatk, libcups, libdrm, etc.). The second
run (without sudo) places the Chromium binary in `~/.cache/ms-playwright/` where the
user can access it.

**Create symlink and desktop launcher:**

```bash
# Symlink to PATH
CHROME_BIN=$(find ~/.cache/ms-playwright/chromium-*/chrome-linux -name chrome -type f | head -1)
ln -sf "$CHROME_BIN" ~/.local/bin/chromium

# Desktop launcher (use unquoted heredoc so $CHROME_BIN expands)
mkdir -p ~/Desktop
cat > ~/Desktop/Chromium.desktop << LAUNCHER
[Desktop Entry]
Type=Application
Name=Chromium
Exec=$CHROME_BIN --no-sandbox
Icon=web-browser
Terminal=false
Categories=Network;WebBrowser;
LAUNCHER
chmod +x ~/Desktop/Chromium.desktop
```

The `--no-sandbox` flag is required when running as a non-root user on headless servers.

**Verify:**

```bash
chromium --version
```

---

## VNC Configuration

### Password

```bash
vncpasswd
```

Sets `~/.vnc/passwd`. No view-only password needed.

### Desktop Session

Create `~/.vnc/xstartup`:

```bash
mkdir -p ~/.vnc
cat > ~/.vnc/xstartup << 'XSTARTUP'
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
thunar --daemon &
exec startxfce4
XSTARTUP
chmod +x ~/.vnc/xstartup
```

The `thunar --daemon` line starts the file manager service before XFCE launches. Without
it, desktop icon double-clicks fail with "requires a file manager service."

---

## Starting and Stopping

**Start VNC on display :1 (port 5901):**

```bash
vncserver :1 -geometry 1920x1080 -depth 24 -localhost no
```

The `-localhost no` flag is critical — without it VNC binds to 127.0.0.1 only.

**Stop:**

```bash
vncserver -kill :1
```

**Verify it's listening externally:**

```bash
ss -tlnp | grep 5901
```

Should show `0.0.0.0:5901`, not `127.0.0.1:5901`.

---

## Network Access

### Tailscale-only access (recommended)

If the server's AWS security group does not expose port 5901, VNC is reachable only via
Tailscale. Tailscale traffic arrives on the `tailscale0` interface and bypasses AWS
security groups entirely — no SG rule needed.

### Public access

> **Warning:** VNC transmits all traffic unencrypted, including keystrokes and screen
> contents. VNC passwords are silently truncated to 8 characters, making brute-force
> feasible. Prefer Tailscale or SSH tunnel access. If public exposure is required,
> restrict the CIDR to your known IPs rather than 0.0.0.0/0.

For servers that need VNC reachable from the public internet, add an inbound rule to the
security group:

```bash
# Get instance and security group IDs
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
INSTANCE_ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id)
SG_ID=$(aws ec2 describe-instances --instance-ids "$INSTANCE_ID" \
  --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text)

# Open port 5901 — replace with your actual IP (run: curl ifconfig.me)
YOUR_IP="<your-ip>/32"
aws ec2 authorize-security-group-ingress \
  --group-id "$SG_ID" --protocol tcp --port 5901 --cidr "$YOUR_IP"
```

Duplicate-rule errors are safe to ignore.

**Verify:**

```bash
aws ec2 describe-security-groups --group-ids "$SG_ID" \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`5901`]' --output table
```

---

## Always-On Mode

For servers where VNC should survive reboots, create a systemd user service.

Enable lingering first so user services start at boot without an active login session:

```bash
sudo loginctl enable-linger $USER
```

Create the service unit:

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/vncserver.service << 'UNIT'
[Unit]
Description=TigerVNC Server
After=network.target

[Service]
Type=forking
ExecStartPre=-/usr/bin/vncserver -kill :1
ExecStart=/usr/bin/vncserver :1 -geometry 1280x800 -depth 24 -localhost no
ExecStop=/usr/bin/vncserver -kill :1
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
UNIT

systemctl --user daemon-reload
systemctl --user enable --now vncserver.service
```

The `ExecStartPre=-` line kills any stale VNC session before starting. The `-` prefix
tells systemd to ignore failures (important — `|| true` does NOT work in systemd unit
files because they don't use a shell).

**Verify:**

```bash
systemctl --user status vncserver.service
ss -tlnp | grep 5901
```

---

## Connecting from macOS

### Built-in Screen Sharing

Finder → Go → Connect to Server (Cmd+K), then enter:

- **Via Tailscale:** `vnc://<tailscale-ip>:5901`
- **Via public IP:** `vnc://<public-ip>:5901`
- **Via SSH tunnel:** `vnc://localhost:5901` (after setting up tunnel below)

Enter the VNC password when prompted.

### SSH Tunnel (encrypted, no port exposure needed)

```bash
ssh -L 5901:localhost:5901 ubuntu@<hostname>
```

Then connect to `vnc://localhost:5901`. This works even when port 5901 is not open in
the security group.

### Third-Party Clients

RealVNC Viewer gives smoother performance than macOS built-in Screen Sharing:

```bash
brew install --cask vnc-viewer  # RealVNC
```

---

## Fleet Reference

| Server  | Mode      | SG Port 5901                |
| ------- | --------- | --------------------------- |
| hex     | always-on | closed (Tailscale-only)     |
| mycroft | always-on | open (sg-0024bf3d80fd63ebb) |
| dristhi | always-on | open (sg-0024bf3d80fd63ebb) |

Connect via Tailscale IP (check `tailscale status`) or hostname.

---

## Troubleshooting

**VNC starts but shows grey screen / no desktop:** Check that `~/.vnc/xstartup` exists,
is executable, and contains `exec startxfce4`.

**"Connection refused" from Mac:** Verify VNC is listening externally
(`ss -tlnp | grep 5901` should show `0.0.0.0`). If it shows `127.0.0.1`, you forgot
`-localhost no`.

**"Failed to run Chromium desktop... requires a file manager service":** Install
`thunar` (`sudo apt install thunar`) and restart the VNC session. XFCE needs a file
manager to handle desktop icon activation.

**Chromium won't launch (snap errors):** Don't use the `chromium-browser` apt package on
Ubuntu 24.04 — it's a snap transitional package that's unreliable in VNC. Use
Playwright's Chromium instead (see Browser section above).

**Display :1 already in use:** Kill the stale session: `vncserver -kill :1` then start
again. The always-on systemd service handles this automatically via `ExecStartPre`.

**systemd `|| true` doesn't work:** Systemd ExecStart/ExecStartPre lines don't run in a
shell. `|| true` gets interpreted as arguments to the command (e.g., ssh tries to
connect to host "true"). Use the `-` prefix on ExecStartPre instead.

---

# Remote Desktop Setup — Linux

**Date:** 2026-03-31 **Status:** Production

VNC-based remote desktop for fleet Linux servers. Provides a lightweight graphical
desktop (Xfce4) with Chromium browser, accessible via VNC client from macOS.

Two modes:

- **Always-on** — for servers that need persistent screen sharing (e.g. hex)
- **On-demand** — start/stop as needed for debugging or browser tasks

---

## Packages

Required apt packages for VNC + desktop:

```
xfce4
xfce4-terminal
dbus-x11
tigervnc-standalone-server
tigervnc-common
chromium-browser
```

These are not in `apt-packages.txt` because not every fleet machine needs a desktop.
Install manually on machines that need it.

**Note:** On Ubuntu 24.04, `chromium-browser` is a transitional package that installs
Chromium via snap. If snapd is disabled or restricted, use `firefox` instead.

**Install:**

```bash
sudo DEBIAN_FRONTEND=noninteractive apt install -y \
  xfce4 xfce4-terminal dbus-x11 \
  tigervnc-standalone-server tigervnc-common \
  chromium-browser
```

**Verify:**

```bash
dpkg -s xfce4 tigervnc-standalone-server chromium-browser 2>&1 | grep -E '^Package:|^Status:'
```

Each package should show `Status: install ok installed`.

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
exec startxfce4
XSTARTUP
chmod +x ~/.vnc/xstartup
```

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

For servers where VNC should survive reboots (e.g. hex), create a systemd user service.

Enable lingering first so user services start at boot without an active login session:

```bash
sudo loginctl enable-linger $USER
```

Create the service unit:

```bash
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/vnc-desktop.service << 'UNIT'
[Unit]
Description=VNC Desktop (Xfce4 on :1)
After=network.target

[Service]
Type=forking
PIDFile=%h/.vnc/%H:1.pid
ExecStart=/usr/bin/vncserver :1 -geometry 1920x1080 -depth 24 -localhost no
ExecStop=/usr/bin/vncserver -kill :1
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
UNIT

systemctl --user daemon-reload
systemctl --user enable --now vnc-desktop.service
```

**Verify:**

```bash
systemctl --user status vnc-desktop.service
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

| Server  | Mode      | SG Port 5901            |
| ------- | --------- | ----------------------- |
| hex     | always-on | closed (Tailscale-only) |
| mycroft | on-demand | open                    |
| dristhi | on-demand | open                    |

Connect via Tailscale IP (check `tailscale status`) or hostname.

---

## Troubleshooting

**VNC starts but shows grey screen / no desktop:** Check that `~/.vnc/xstartup` exists,
is executable, and contains `exec startxfce4`.

**"Connection refused" from Mac:** Verify VNC is listening externally
(`ss -tlnp | grep 5901` should show `0.0.0.0`). If it shows `127.0.0.1`, you forgot
`-localhost no`.

**Chromium won't launch (snap errors):** On Ubuntu 24.04, chromium-browser is a snap
package. If it fails inside VNC, try: `snap run chromium` or install Firefox as
fallback: `sudo apt install firefox`.

**Display :1 already in use:** Kill the stale session: `vncserver -kill :1` then start
again.

---

**Maintained by:** Hex **Last updated:** 2026-03-31

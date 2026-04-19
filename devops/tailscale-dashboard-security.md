# Securing OpenClaw Dashboard on Tailscale

## Overview

Expose the OpenClaw Control UI over HTTPS on Tailscale with tailnet-only access. No
public internet exposure.

This solves the core problem: browsers block `window.crypto.subtle` (Web Crypto API) on
non-secure contexts. Without HTTPS, the Control UI can't complete device identity checks
and gets stuck at the login page.

**Architecture:** Gateway binds to loopback → Tailscale Serve proxies HTTPS on port 443
to `127.0.0.1:18789` → Tailscale's DNS resolves MagicDNS hostnames to 100.x IPs.

---

## Step 1: DNS Setup (Required for Homebrew-installed Tailscale)

The Homebrew `tailscale` formula uses the `utun` interface (no system/network
extension). This means Tailscale can't intercept DNS queries at the OS level. Without
intervention, `*.ts.net` hostnames resolve to Tailscale's public ingress IPs (209.x)
instead of tailnet IPs (100.x), and `tailscale serve` silently fails.

**Fix:** Create a macOS resolver file that routes `*.ts.net` queries to Tailscale's DNS:

```bash
sudo mkdir -p /etc/resolver
echo "nameserver 100.100.100.100" | sudo tee /etc/resolver/ts.net
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder 2>/dev/null || true
```

**Verify:**

```bash
# System resolver (NOT dig or nslookup — they bypass the system resolver)
python3 -c "import socket; print(socket.getaddrinfo('your-host.your-tailnet.ts.net', 443)[0][4][0])"
# Should print: 100.x.x.x

# Or use curl
curl -sS --max-time 5 https://your-host.your-tailnet.ts.net/ -o /dev/null -w "%{remote_ip}\n"
# Should print: 100.x.x.x
```

> **Note:** `dig` and `nslookup` bypass the macOS system resolver and won't show the
> correct IP. Use `python3`, `curl`, or Node.js to test — these use the system resolver.

**Persistence:** This file survives reboots. Deploy it as part of machine setup.

---

## Step 2: Set Up Tailscale Serve

```bash
# Clean any existing config
tailscale funnel reset 2>/dev/null || true
tailscale serve reset 2>/dev/null || true

# Set up serve (tailnet-only)
tailscale serve --bg --https=443 http://127.0.0.1:18789
```

**Verify:**

```bash
tailscale serve status --json
# Should show HTTPS on 443, proxy to http://127.0.0.1:18789
# Should NOT have AllowFunnel key
```

**Persistence:** `tailscale serve --bg` persists in Tailscale's state. Survives gateway
restarts and reboots (Tailscale starts at login).

---

## Step 3: Gateway Config

```json5
{
  gateway: {
    port: 18789,
    mode: "local",
    bind: "loopback",
    auth: {
      mode: "token",
      token: "<generate-with: openssl rand -hex 32>",
      password: "<fallback-password>",
    },
    tailscale: {
      mode: "off",
      resetOnExit: true,
    },
    controlUi: {
      enabled: true,
      dangerouslyDisableDeviceAuth: false,
      allowedOrigins: ["https://<your-machine>.<tailnet>.ts.net"],
    },
  },
}
```

Key points:

- **`bind: loopback`** — gateway only on 127.0.0.1. Tailscale is the only way in.
- **`auth.mode: token`** — strong shared secret required for each connection. Set both
  `token` and `password` for two-factor auth (token + password).
- **`dangerouslyDisableDeviceAuth: false`** — device identity checks are active. HTTPS
  from Tailscale Serve provides the secure context needed for Web Crypto.
- **`allowedOrigins`** — restricted to the MagicDNS hostname over HTTPS.

### Access

Open in browser:

```
https://<your-machine>.<tailnet>.ts.net/
```

The Control UI connects via WebSocket. Enter:

1. **Gateway Token** — the `openssl rand -hex 32` value from config
2. **Password** — the fallback password from config

---

## Alternative: Funnel (Public Internet — Use Only If Serve Doesn't Work)

If the DNS fix in Step 1 doesn't work (e.g. on a Linux machine without `/etc/resolver`),
use `tailscale funnel` as a fallback. This exposes the dashboard to the **public
internet** via Tailscale's proxy servers, but gateway auth still protects it.

```bash
tailscale funnel --bg --https=443 http://127.0.0.1:18789
```

Security implications:

- Anyone on the internet who discovers the URL can attempt authentication
- Password-only auth (device auth is auto-approved for loopback connections)
- Tailscale's proxy servers see unencrypted HTTP traffic between their edge and your
  machine
- Use a **strong** password if funnel is required

---

## Troubleshooting

### Serve config disappears immediately

**Symptom:** `tailscale serve --bg` reports success, but `tailscale serve status --json`
returns `{}`.

**Cause:** DNS not intercepting `*.ts.net` queries. Without the resolver file, the
system resolves the hostname to public IPs, and Tailscale's daemon discards the serve
config.

**Fix:** Apply Step 1 (DNS setup).

### Etag mismatch errors

**Symptom:** "Another client is changing the serve config" or "preconditions failed:
etag mismatch."

**Cause:** Race condition between multiple Tailscale processes.

**Fix:**

```bash
tailscale funnel reset 2>/dev/null; tailscale serve reset 2>/dev/null
sleep 2
tailscale serve --bg --https=443 http://127.0.0.1:18789
```

### DNS resolves to 209.x instead of 100.x

**Symptom:** curl or browser gets `SSL_ERROR_SYSCALL` or connection refused.

**Cause:** `/etc/resolver/ts.net` missing or Tailscale not running.

**Diagnose:**

```bash
# Check resolver file exists
cat /etc/resolver/ts.net  # should show: nameserver 100.100.100.100

# Check Tailscale DNS directly
nslookup <hostname>.ts.net 100.100.100.100

# Check system resolver
python3 -c "import socket; print(socket.getaddrinfo('<hostname>.ts.net', 443)[0][4][0])"
```

### Gateway bind:loopback still listens on all interfaces

**Symptom:** `lsof -Pn -i :18789` shows `*:18789`.

**Cause:** Gateway needs full restart to rebind.

**Fix:**

```bash
openclaw gateway restart
sleep 3
lsof -Pn -i :18789 | grep LISTEN
# Should show: 127.0.0.1:18789
```

---

## Security Summary

| Layer     | What protects you                                 |
| --------- | ------------------------------------------------- |
| Network   | Tailnet only — not reachable from public internet |
| Transport | HTTPS via Tailscale Serve (Let's Encrypt certs)   |
| Auth      | Gateway token (shared secret) + password          |
| Device    | Browser-bound device identity via Web Crypto      |
| Origin    | Only `https://<hostname>.ts.net` accepted         |

**Do not set `dangerouslyDisableDeviceAuth: true`** unless in a break-glass emergency.
The HTTPS context from Tailscale Serve makes device auth work without issues.

**Do not use `bind: lan` or `bind: tailnet`** with serve — always use `bind: loopback`
so Tailscale is the only ingress path.

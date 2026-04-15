# Securing OpenClaw Dashboard on Tailscale

## Overview

Two approaches to expose the OpenClaw Control UI over HTTPS on Tailscale. Choose the one
that matches your machine's state.

| Approach        | When to use                                          | Access scope |
| --------------- | ---------------------------------------------------- | ------------ |
| **Serve + TLS** | Tailscale network extension is installed and working | Tailnet only |
| **Funnel**      | Network extension missing or DNS resolution broken   | Public\*     |

\* Funnel is public, but gateway password auth still protects access.

Both approaches solve the same underlying problem: browsers block `window.crypto.subtle`
(Web Crypto API) on non-secure contexts. Without HTTPS, the Control UI can't complete
device identity checks and gets stuck at the login page.

---

## Approach 1: Serve + TLS (Preferred)

Requires the Tailscale **network extension** to be installed and active. This intercepts
MagicDNS queries so `*.ts.net` hostnames resolve to the local Tailscale IP (100.x)
instead of public ingress IPs.

### Prerequisites

1. Network extension installed and loaded:

```bash
systemextensionsctl list | grep -i tailscale
# Should show at least 1 Tailscale extension
```

2. MagicDNS resolves to 100.x:

```bash
dig +short <your-machine>.<tailnet>.ts.net
# Should return 100.x.x.x, not 209.x.x.x
```

If either check fails, use **Approach 2 (Funnel)** instead.

### Steps

```bash
# Generate Tailscale TLS certs
MAGICDNS="<your-machine>.<tailnet>.ts.net"
mkdir -p ~/.openclaw/tls
cd ~/.openclaw/tls
tailscale cert "$MAGICDNS"
mv "$MAGICDNS.crt" server.crt
mv "$MAGICDNS.key" server.key

# Set up tailscale serve (proxy to loopback gateway)
tailscale serve --bg --https=443 http://127.0.0.1:18789
```

### Gateway Config

```json5
"gateway": {
  "bind": "loopback",
  "auth": {
    "mode": "password",
    "password": "<choose-password>"
  },
  "tls": {
    "enabled": true,
    "certPath": "/Users/<user>/.openclaw/tls/server.crt",
    "keyPath": "/Users/<user>/.openclaw/tls/server.key"
  },
  "tailscale": {
    "mode": "off",
    "resetOnExit": false
  },
  "controlUi": {
    "enabled": true,
    "allowedOrigins": [
      "https://<your-machine>.<tailnet>.ts.net"
    ]
  }
}
```

### Verify

```bash
tailscale serve status --json   # should show proxy config
curl -sS https://<your-machine>.<tailnet>.ts.net/ | head -5  # HTTP 200
```

---

## Approach 2: Funnel (When Network Extension Is Missing)

Uses Tailscale's public proxy servers instead of local DNS interception. No network
extension required.

**Why network extensions go missing:** On macOS, the Tailscale app may be installed
without the system extension (e.g. Mac App Store version, or the extension was removed
in Privacy & Security settings). Without it, MagicDNS queries for `*.ts.net` fall
through to the local resolver and return Tailscale's public ingress IPs (209.x) instead
of the tailnet IP (100.x). `tailscale serve` can't intercept traffic that never reaches
the local machine.

**Check:** `systemextensionsctl list` — if it shows 0 Tailscale extensions, use this
approach.

### Steps

```bash
# Set up funnel (proxies through Tailscale's public servers)
tailscale funnel --bg --https=443 http://127.0.0.1:18789
```

### Gateway Config

```json5
"gateway": {
  "bind": "loopback",
  "auth": {
    "mode": "password",
    "password": "<choose-password>"
  },
  "tailscale": {
    "mode": "off",
    "resetOnExit": false
  },
  "controlUi": {
    "enabled": true,
    "dangerouslyDisableDeviceAuth": true,
    "allowedOrigins": [
      "https://<your-machine>.<tailnet>.ts.net"
    ]
  }
}
```

### Verify

```bash
tailscale funnel status --json   # should show AllowFunnel config
curl -sS https://<your-machine>.<tailnet>.ts.net/ | head -5  # HTTP 200
```

---

## Persistence Across Restarts

`tailscale funnel --bg` persists in Tailscale's state and survives gateway restarts. It
also survives reboots because Tailscale itself starts at login.

No additional launchd agents are needed — Tailscale manages the funnel config
internally.

### Tailscale App Auto-Start

Make sure Tailscale launches at login:

```bash
# Verify Tailscale is set to open at login
osascript -e 'tell application "System Events" to get the name of every login item' | grep -i tailscale
```

If missing, add it via System Settings > General > Login Items, or:

```bash
osascript -e 'tell application "System Events" to make login item at end with properties {path:"/Applications/Tailscale.app", hidden:false}'
```

---

## Troubleshooting

### Serve config disappears immediately

**Symptom:** `tailscale serve --bg` reports success, but `tailscale serve status --json`
returns `{}` right after.

**Cause:** Tailscale network extension is not installed. The serve config needs the
network extension to route traffic through WireGuard. Without it, the daemon discards
the config.

**Fix:** Use `tailscale funnel` instead (Approach 2), or install the network extension.

### Etag mismatch errors

**Symptom:** `tailscale funnel` or `tailscale serve` returns "Another client is changing
the serve config" or "preconditions failed: etag mismatch."

**Cause:** Race condition between multiple Tailscale processes (CLI, app UI).

**Fix:**

```bash
tailscale funnel reset
tailscale serve reset
sleep 2
tailscale funnel --bg --https=443 http://127.0.0.1:18789
```

### DNS resolves to 209.x instead of 100.x

**Symptom:** `dig +short <hostname>.ts.net` returns 209.177.x.x addresses.

**Cause:** Tailscale network extension not intercepting DNS for `*.ts.net`.

**Diagnose:**

```bash
# Check DNS config
scutil --dns | grep -A3 tailscale
# If "reach: 0x00000000 (Not Reachable)" — extension not loaded

# Check Tailscale's DNS directly
nslookup <hostname>.ts.net 100.100.100.100
# If this returns 100.x — Tailscale DNS works, but macOS isn't using it
```

**Fix:** Use funnel (Approach 2), or install the network extension.

### Gateway bind:loopback still listens on all interfaces

**Symptom:** `lsof -Pn -i :18789` shows `*:18789` instead of `127.0.0.1:18789`.

**Cause:** Gateway may need a full restart (not just SIGUSR1 reload) to rebind.

**Fix:**

```bash
openclaw gateway restart
sleep 3
lsof -Pn -i :18789 | grep LISTEN
# Should show 127.0.0.1:18789
```

---

## Security Notes

- **Loopback bind is mandatory.** Always bind the gateway to `loopback` so Tailscale is
  the only way in. Never bind to `lan` or `tailnet` when using funnel.
- **Password auth protects funnel access.** Even though funnel is public, the gateway
  password (`million1` or stronger) is required.
- **`dangerouslyDisableDeviceAuth`** is needed with funnel because the device identity
  check relies on Web Crypto APIs that require a secure context with loopback bind. Keep
  this true when using funnel; turn it off when using Approach 1 (Serve + TLS).
- **Upgrade path:** When the Tailscale network extension is available, switch to
  Approach 1 (Serve + TLS) and remove `dangerouslyDisableDeviceAuth`.

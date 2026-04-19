# Tailscale + macOS DNS Troubleshooting (Homebrew Install)

## The Problem

When Tailscale is installed via Homebrew (`brew install tailscale`), it uses the `utun`
kernel interface instead of a macOS system/network extension. This works fine for VPN
connectivity but **breaks DNS interception**.

Without DNS interception, `*.ts.net` MagicDNS hostnames resolve to Tailscale's public
ingress IPs (209.x) instead of tailnet IPs (100.x). This causes:

- `tailscale serve` to silently discard its config (returns `{}` immediately)
- `curl` or browsers get `SSL_ERROR_SYSCALL` or `ERR_CONNECTION_CLOSED`
- `dig` and `nslookup` show the wrong IPs

## Why It Happens

On macOS, Tailscale has three installation variants:

| Variant                | DNS Mechanism         | Install Method           |
| ---------------------- | --------------------- | ------------------------ |
| App Store / Standalone | Network Extension     | `.pkg` or App Store      |
| Homebrew (headless)    | `utun` (no extension) | `brew install tailscale` |

The network extension intercepts `*.ts.net` DNS queries and routes them to
`100.100.100.100` (Tailscale's DNS). Without it, queries go to the system's default
resolver (usually your router), which returns public IPs.

## The Fix

Create a macOS resolver file that tells the system DNS to use Tailscale's nameserver for
`*.ts.net` queries:

```bash
sudo mkdir -p /etc/resolver
echo "nameserver 100.100.100.100" | sudo tee /etc/resolver/ts.net
```

Flush DNS cache:

```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder 2>/dev/null || true
```

### Where to Run This

**On every machine** that needs to resolve `*.ts.net` hostnames:

- The server hosting `tailscale serve`
- Every client machine (laptop, desktop) that accesses the dashboard
- Any machine running scripts that connect to `*.ts.net` URLs

The server-side fix enables `tailscale serve` to persist. The client-side fix enables
browsers and CLI tools to reach the dashboard.

### Persistence

`/etc/resolver/ts.net` survives reboots. No launchd agent or cron job needed.

## How to Verify

**Do NOT use `dig` or `nslookup`** — they bypass the macOS system resolver and always
show the public IPs. Use tools that go through the system resolver:

```bash
# Python (uses system resolver)
python3 -c "import socket; print(socket.getaddrinfo('<hostname>.ts.net', 443)[0][4][0])"

# curl (uses system resolver)
curl -sS --max-time 5 https://<hostname>.ts.net/ -o /dev/null -w "%{remote_ip}\n"

# Node.js (uses system resolver via getaddrinfo)
node -e "require('dns').lookup('<hostname>.ts.net', (e,addr) => console.log(addr))"
```

Expected: `100.x.x.x` (tailnet IP)

Wrong: `209.x.x.x` (public ingress IP)

## Diagnosing

Check if the resolver file is configured:

```bash
scutil --dns | grep -A3 'ts.net'
```

Expected output includes:

```
domain   : ts.net
nameserver[0] : 100.100.100.100
flags    : Request A records
reach    : 0x00000002 (Reachable)
```

If `reach` shows `0x00000000 (Not Reachable)`, the file exists but Tailscale's DNS
server isn't responding (check `tailscale status`).

## Common Mistakes

### Using `dig` to test DNS

`dig` has its own DNS resolver stack and bypasses `/etc/resolver/`. It will always show
the public IPs. This is expected and does NOT mean the fix is broken.

### Setting up serve before the DNS fix

If `tailscale serve --bg` reports success but `tailscale serve status --json` returns
`{}`, the DNS fix is missing. Tailscale's daemon checks DNS resolution before committing
the serve config.

### Applying the fix on the server only

Each machine that accesses the dashboard needs the fix. A laptop without
`/etc/resolver/ts.net` will resolve to public IPs and get connection errors.

## Related Docs

- [Tailscale macOS Variants](https://tailscale.com/docs/concepts/macos-variants)
- [Tailscale Serve](https://tailscale.com/kb/1312/serve)
- [OpenClaw Dashboard Security](./tailscale-dashboard-security.md)

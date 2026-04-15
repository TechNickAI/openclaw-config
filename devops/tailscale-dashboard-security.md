# Securing OpenClaw Dashboard on Tailscale (Best Practices)

## Objective

Safely expose the OpenClaw Gateway Dashboard to your Tailscale network (tailnet) with
end-to-end encryption, browser compatibility for Web Crypto APIs (WebSockets device
identity), and strict access controls.

## Research & The Problem

When accessing the OpenClaw Dashboard via HTTP over an IP address (e.g.,
`http://<tailscale-ip>:18789`), modern browsers block operations under
`window.crypto.subtle` (the Web Crypto API) if the originating connection is not
considered a "Secure Context". This prevents the necessary device identity checks from
completing, trapping the user at the login page.

While it is possible to bypass the check using `dangerouslyDisableDeviceAuth = true`,
doing so compromises defense-in-depth measures.

Another option is to proxy the connection through `tailscale serve`. While this
correctly provisions Let's Encrypt certificates and establishes HTTPS, we encountered
proxy loops and connection resets on macOS.

## The Solution

The most secure, industry-standard approach for Tailscale applications without proxy
sidecars is to:

1. **Bind locally to the Tailnet interface** so the gateway daemon drops any traffic
   from the local physical LAN (`192.168...`) or the public web.
2. **Terminate TLS natively in the OpenClaw Gateway** by providing the gateway the
   cryptographic material (`.crt`, `.key`) provided by Tailscale's MagicDNS.
3. **Use a gateway password** as an explicit multi-factor check instead of just an
   opaque token.

### Implementation Steps

#### Generate local Tailscale Certificates

Retrieve the trusted TLS certificates specifically for your Tailscale node's MagicDNS
hostname (e.g., `<your-machine>.<tailnet>.ts.net`).

```bash
# Verify the MagicDNS name
tailscale status --json | jq .Self.MagicDNSSuffix

# Fetch the certificates (substitute your own MagicDNS hostname)
MAGICDNS="<your-machine>.<tailnet>.ts.net"
mkdir -p ~/.openclaw/tls
cd ~/.openclaw/tls
tailscale cert "$MAGICDNS"

# Rename them for convenience
mv "$MAGICDNS.crt" server.crt
mv "$MAGICDNS.key" server.key
```

#### Apply Secure OpenClaw Settings

Configure your `~/.openclaw/openclaw.json` (or use `openclaw config set`) with the
following block under the `gateway` key. Replace `<your-machine>.<tailnet>.ts.net` with
your MagicDNS hostname and `$HOME` with your actual home directory path:

```json5
"gateway": {
  "port": 18789,
  "mode": "local",
  "bind": "tailnet",
  "auth": {
    "mode": "password",
    "password": "<choose-a-strong-password>"
  },
  "tls": {
    "enabled": true,
    "certPath": "$HOME/.openclaw/tls/server.crt",
    "keyPath": "$HOME/.openclaw/tls/server.key"
  },
  "tailscale": {
    "mode": "off",
    "resetOnExit": false
  },
  "controlUi": {
    "enabled": true,
    "allowedOrigins": [
      // Allow only the specific MagicDNS name over HTTPS
      "https://<your-machine>.<tailnet>.ts.net:18789"
    ]
  }
}
```

Note: paths in `openclaw.json` must be absolute — `$HOME` above is shown for
readability; substitute the expanded path (e.g., `/Users/you/.openclaw/tls/server.crt`)
when saving.

#### Access

Your dashboard is now secured natively via HTTPS and can be accessed seamlessly over the
Tailnet at:

**`https://<your-machine>.<tailnet>.ts.net:18789`**

Use the configured password to authenticate. Device identity WebCrypto operations pass
without error thanks to a native "Secure Context."

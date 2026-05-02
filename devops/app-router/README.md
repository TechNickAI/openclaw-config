# App Router

A lightweight pattern for spinning up named web apps on any fleet machine and serving
them at a clean URL — with optional per-app password protection. No cloud required.
Works from a phone.

## What It Does

Every app gets a path like `/my-app/` on a single Tailscale HTTPS URL. A visitor who
hits a password-protected app sees a clean login form asking for a password by the app's
friendly name — not a technical slug. Entering the correct password sets a scoped cookie
that grants access only to that app, not any other.

Under the hood: PM2 keeps the Node processes alive. Caddy sits in front of them as a
path router and handles the auth challenge via `forward_auth`. A small Express sidecar
(`auth-service/`) issues and validates the session cookies. Tailscale Serve provides
HTTPS with no certificate management.

## Layout

```
devops/app-router/
  auth-service/    Express auth sidecar (server.js + tests)
  templates/       Caddyfile and ecosystem.config.js examples
  scripts/         restore-tailscale-serve.sh (wired into launchd)
  launchd/         Plist that re-applies Tailscale Serve on boot
```

The deploy target on each machine is `~/openclaw-apps/`:

```
~/openclaw-apps/
  ecosystem.config.js              copy of templates/ecosystem.config.js.example
  auth-service/                    copy of devops/app-router/auth-service/
  _registry/
    Caddyfile                      copy of templates/Caddyfile.example
    restore-tailscale-serve.sh     copy of scripts/restore-tailscale-serve.sh
    logs/                          stdout/stderr for the launchd plist
  <app-name>/                      one directory per app
```

## First-Time Setup on a New Machine

Install Caddy via Homebrew and PM2 globally via npm:

```
brew install caddy
npm install -g pm2
```

Run the install helper from the repo root — it copies the templates, installs
auth-service deps, and stages the launchd plist with `<USER>` substituted:

```
bash devops/app-router/scripts/install.sh
```

Re-running is safe; existing files are skipped. Pass `--force` to overwrite.

Edit `~/openclaw-apps/ecosystem.config.js` — set `AUTH_SECRET` (use
`openssl rand -hex 32`), and fill in `APP_PASSWORD_<SLUG>`, `APP_TITLE_<SLUG>`, and
`APP_DESC_<SLUG>` for any protected apps. Then edit
`~/openclaw-apps/_registry/Caddyfile` to match.

Start everything under PM2:

```
pm2 start ~/openclaw-apps/ecosystem.config.js
pm2 start /opt/homebrew/bin/caddy --name caddy --interpreter none -- \
  run --config ~/openclaw-apps/_registry/Caddyfile --adapter caddyfile
pm2 save
pm2 startup     # then run the printed sudo command
```

Point Tailscale Serve at Caddy:

```
tailscale serve --bg --https=4242 http://127.0.0.1:8080
```

Tailscale Serve config does not survive reboots on its own. The install helper already
staged the launchd plist with your `$USER` substituted; load it now:

```
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.openclaw.app-router-serve.plist
```

Verify everything is working — replace `<host>` with your Tailscale hostname:

```
curl https://<host>:4242/health     # → "ok"
```

## Adding an App

Each app is a process (Node, Python, anything that binds to localhost) and a slot in two
files: `ecosystem.config.js` and the Caddyfile.

**In `ecosystem.config.js`**, append to the `apps` array with the process name, script
path, working directory, and `env.PORT`. If the app is password-protected, also add
`APP_PASSWORD_<SLUG>`, `APP_TITLE_<SLUG>`, and `APP_DESC_<SLUG>` to the auth-service
`env` block. The slug is the app's URL segment uppercased with `-` replaced by `_`.

**In the Caddyfile**, add a `handle` block for the new path. Open apps just strip the
prefix and reverse-proxy. Password-protected apps add a `forward_auth` block pointing at
`127.0.0.1:3000/auth/verify?app=<slug>` that redirects to `/auth/login?app=<slug>` on
401, then strip the prefix and proxy.

After editing both files:

```
pm2 restart ecosystem.config.js          # or just `pm2 restart auth-service` for password-only changes
caddy reload --config ~/openclaw-apps/_registry/Caddyfile --adapter caddyfile
```

The app is immediately live at `https://<host>:4242/<slug>/`.

## Removing an App

```
pm2 delete <name>
```

Then drop its `handle` block from the Caddyfile, its entry from `ecosystem.config.js`,
and its `APP_*_<SLUG>` env vars from the auth-service block. Reload PM2 and Caddy as
above.

## Auth Model

Apps have three modes:

- **Open** — no password. Omit the app from the auth-service env entirely and use a
  plain `handle` block in the Caddyfile.
- **Password-protected** — a single shared password. Set `APP_PASSWORD_<SLUG>`. Anyone
  who knows it gets a 7-day cookie scoped to that app's path only. Knowing one app's
  password grants no access to any other app.
- **No-password configured** — if the Caddyfile has a `forward_auth` block but
  `APP_PASSWORD_<SLUG>` is unset, the auth service treats the app as open. Useful during
  development.

The auth service signs cookies with `AUTH_SECRET`. If unset and `NODE_ENV=production`,
the service refuses to start; pass `AUTH_ALLOW_RANDOM_SECRET=1` to opt into ephemeral
sessions (a random secret is generated each boot, so every restart logs everyone out).
Outside production, an unset `AUTH_SECRET` falls back to a random value with a warning.
Each machine should have its own secret.

The login POST endpoint is rate-limited to 30 attempts per IP per minute and rejects
requests whose `Origin`/`Referer` doesn't match the request host (mitigates CSRF beyond
SameSite=lax). 401s and CSRF rejections are logged to stdout with slug + IP, captured by
PM2.

Slugs are validated against `^[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?$` — lowercase
alphanumerics and hyphens, max 32 chars. Anything outside that gets a 400 from
`/auth/verify` and `/auth/login`.

## Public Access

Tailscale Serve is tailnet-only. To make an app accessible from outside the tailnet
(sharing with people who aren't on Tailscale), use Tailscale Funnel on a separate port:

```
tailscale funnel --bg --https=4243 http://127.0.0.1:8080
```

All apps on the router become accessible at the funnel URL — gate anything sensitive
behind a password before flipping that on.

## Fleet Notes

Each machine runs its own independent app router. There is no central router. If an app
needs data from a specific machine, it runs on that machine. The Tailscale hostname
makes it obvious which machine you're hitting.

The `AUTH_SECRET` should be different per machine. Either generate a fresh one with
`openssl rand -hex 32` or omit it and accept that auth-service restarts invalidate
sessions.

## Port Conventions

- `3000` — auth service
- `8080` — Caddy
- `3001+` — apps

Comment each app's port in `ecosystem.config.js` to avoid collisions when adding new
apps.

## Tests

The auth service has unit tests for the security-critical functions (slug validation,
HTML escaping, open-redirect guard, timing-safe compare):

```
cd devops/app-router/auth-service
npm install
npm test
```

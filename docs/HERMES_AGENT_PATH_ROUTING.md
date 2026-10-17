# Hermes Agent Dashboard at `https://hermes.kcb.vn/agent`

**Status: Prepared in GitHub; NOT deployed. Nothing here has been run against Rocky.**
Explicit operator approval is required for each production step below.

| URL | Service |
|---|---|
| `/` | Hermes Platform (`hermes-website.service`, 127.0.0.1:8099) |
| `/chat` | Platform chatbot (unchanged, served by the default `handle`) |
| `/agent` | Original Nous Research Hermes Agent Dashboard (127.0.0.1:19119) |

## Why no adapter is needed (verified in source)

Upstream commit `d923a5eb487a17c0a68801bba9ef0f56c81040a8` (tag `abandoned-rc.1-v0.22.2`, the version
running on Rocky) supports mounting under a path through the `X-Forwarded-Prefix` request header:

- `hermes_cli/dashboard_auth/prefix.py` validates the prefix (single source of truth).
- `hermes_cli/web_server_dashboard.py` rewrites the served `index.html` (absolute asset URLs) and injects
  `window.__HERMES_BASE_PATH__`; `web/src/lib/api.ts` reads it for API and WebSocket URLs. No rebuild.
- `hermes_cli/dashboard_auth/{login_page,routes,middleware}.py` apply the prefix to login HTML (fonts),
  redirects and the cookie name/`Path`.
- `HERMES_DASHBOARD_PUBLIC_URL` / `dashboard.public_url` declares the complete public URL
  (`https://hermes.kcb.vn/agent`); it is used verbatim for auth redirects and the Host/Origin guard.

Not verified (no access to Rocky): that every page and the PTY/chat WebSockets work through the prefix in a
real browser. Treat as untested until the acceptance checklist is done.

## Conflict with the earlier cutover document

`HERMES_DASHBOARD_PRODUCTION_CUTOVER.md` states "Do not expose this administration surface via Caddy".
This runbook deliberately supersedes that line **only** for `/agent`, and only with the controls below.
The Dashboard can run tools, so the auth gate alone is not enough.

## Decision required before applying: access control

Choose one and record it in the PR:

1. **VPN/Tailscale only** (recommended): Caddy `/agent/*` accepts only the VPN CIDR.
2. **IP allowlist** of stable office/operator addresses (uncomment the `@denied` lines in the template).
3. Dashboard Basic Auth only (weakest; internet-reachable admin surface).

Port 19119 stays bound to `127.0.0.1` (already so in `compose.dashboard-production.yaml`); never open it.

## Apply (requires approval; maintenance window)

The dashboard runs **inside the production gateway container** (`hermes`), so changing its environment
recreates that container and briefly interrupts the gateway.

1. Backup + baseline: record `docker inspect hermes-platform-agent` image digest and restart count (no env
   dump); verify the volume backup per `BACKUP_RECOVERY.md`.
2. Set in `deploy/rocky/dashboard-production.env` (never commit): `HERMES_DASHBOARD_PUBLIC_URL=https://hermes.kcb.vn/agent`.
   Caddy reaches the container over the Docker bridge, so loopback trust may not apply to its source IP; the
   public URL (or `dashboard.trusted_proxies` with the exact proxy IP) makes the forwarded headers usable.
   Confirm in the first test whether an empty value is treated as unset before leaving it blank elsewhere.
3. Recreate (approved): `docker compose -f deploy/rocky/compose.yaml -f deploy/rocky/compose.dashboard-production.yaml up -d --no-deps hermes`.
4. Back up Caddy to a path **outside** the import globs:
   `sudo install -d -m 700 /root/caddy-backups && sudo cp -a /etc/caddy/conf.d/hermes-website.caddy /root/caddy-backups/hermes-website.caddy.$(date +%Y%m%d-%H%M)`.
5. Edit only the `hermes.kcb.vn` block from `deploy/rocky/caddy/hermes-website.caddy.example` (with the chosen
   access policy). Then `sudo caddy validate --config /etc/caddy/Caddyfile` and, only if valid,
   `sudo systemctl reload caddy`. Never restart Caddy; other sites share it.
6. `sh scripts/agent-path-smoke.sh`, then the manual checklist.

## Rollback

1. Restore the Caddy backup file, `sudo caddy validate --config /etc/caddy/Caddyfile`, `sudo systemctl reload caddy`.
2. If the env change must also be undone: clear `HERMES_DASHBOARD_PUBLIC_URL`, re-run the approved compose
   command (second brief gateway interruption). No `down -v`, no volume pruning.
3. Re-run `sh scripts/agent-path-smoke.sh` and confirm `/`, `/chat` and the other sites.

## Acceptance checklist (browser, authenticated)

- [ ] `/` and `/chat` unchanged; `dm.kcb.vn`, `fleet.kcb.vn`, `bot.kcb.vn` still healthy
- [ ] `/agent/` shows login with fonts; login, page refresh on a sub-route, logout work
- [ ] No 404 for CSS/JS/fonts in DevTools; cookie `Path` is `/agent`, Platform session cookies untouched
- [ ] Dashboard pages that call the API work; chat/PTY and `/agent/api/display/ws` WebSockets connect
- [ ] Unauthenticated HTTP **and** WebSocket requests are refused; nothing admin reachable at hostname root
- [ ] `ss -ltnp | grep 19119` shows only `127.0.0.1`
- [ ] Gateway model/provider and a live inference unchanged after the recreate

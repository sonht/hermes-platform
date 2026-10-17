# Hermes Agent Dashboard at `https://hermes.kcb.vn/agent`

**Status: DEPLOYED on Rocky (byt1) 2026-10-17 ~18:37 +07, Tailscale-only.** Approved by the project
owner 2026-10-17 (access policy: VPN/Tailscale only; one recreate of the `hermes` container).

| URL | Service |
|---|---|
| `/` | Hermes Platform (`hermes-website.service`, 127.0.0.1:8099) |
| `/api/public/chat` | Platform public chat API (unchanged, default `handle`) |
| `/agent` | Original Nous Research Hermes Agent Dashboard (127.0.0.1:19119), **tailnet only** |

## Why no adapter is needed (verified in source)

Upstream commit `d923a5eb487a17c0a68801bba9ef0f56c81040a8` (tag `abandoned-rc.1-v0.22.2`, the version
running on Rocky) supports mounting under a path through the `X-Forwarded-Prefix` request header:

- `hermes_cli/dashboard_auth/prefix.py` validates the prefix (single source of truth). The header is read
  directly from the request; it does not depend on `trusted_proxies`.
- `hermes_cli/web_server_dashboard.py` rewrites the served `index.html` (absolute asset URLs) and injects
  `window.__HERMES_BASE_PATH__`; `web/src/lib/api.ts` reads it for API and WebSocket URLs. No rebuild.
- `hermes_cli/dashboard_auth/{login_page,routes,middleware,cookies}.py` apply the prefix to login HTML
  (fonts), redirects and the cookie name/`Path`.
- `HERMES_DASHBOARD_PUBLIC_URL` declares the complete public URL (`https://hermes.kcb.vn/agent`); it is used
  verbatim for auth redirects and the Host guard. Blank counts as unset (`resolve_public_url`).

## Conflict with the earlier cutover document

`HERMES_DASHBOARD_PRODUCTION_CUTOVER.md` states "Do not expose this administration surface via Caddy".
This runbook supersedes that line **only** for `/agent`, and only with the controls below.

## Access control (as deployed)

Facts measured on Rocky before deciding (not assumed):

- Tailscale: tailnet `tail41d4c3.ts.net`, Rocky = `100.110.57.61` / `fd7a:115c:a1e0::c62b:393e`.
  No exit node, no subnet routes. Tailscale's `ts-input` firewall drops `100.64.0.0/10` arriving on any
  interface other than `tailscale0`, so that source range cannot be spoofed from eth0.
- `hermes.kcb.vn` resolves publicly to `160.191.85.228`; there is no split DNS for `kcb.vn` in the tailnet.
- **Every public request reaches Caddy from the NAT address `10.11.1.213`**, with no `X-Forwarded-For`
  (1,749 requests in 24 h of `hsba.kcb.vn` logs). The real client IP is not available to Caddy.
  Never allow `10.11.1.0/24` or `10.11.1.213`: that would open `/agent` to the whole internet.
- Caddy listens on `*:443`, including `tailscale0`.

Rule: inside `handle_path /agent/*`, `not remote_ip 100.64.0.0/10 fd7a:115c:a1e0::/48` → `403`.
Consequence: through public DNS `/agent/*` is **always 403**, even with Tailscale running. To use the
dashboard, a tailnet device must resolve `hermes.kcb.vn` to Rocky's tailnet IP, e.g. on macOS/Linux:

```
# /etc/hosts on the operator's device (Tailscale connected)
100.110.57.61  hermes.kcb.vn
```

The TLS certificate stays valid (same hostname). On that device `/` and the public chat also go via the
tailnet to the same backend. Alternative (not configured): Tailscale admin console → DNS → split DNS /
custom record for `hermes.kcb.vn`. The bare `/agent` 308 redirect is answered for everyone (reveals only
that the path exists); everything under `/agent/` is denied.

Port 19119 stays bound to `127.0.0.1` (`compose.dashboard-production.yaml`); never open it.

### Proxy trust (cookie `Secure`)

Caddy runs on the host and reaches the container through docker-proxy, so the dashboard sees the peer
`172.23.0.1` (gateway of `hermes-platform_hermes_internal`), not loopback. Upstream only honours
`X-Forwarded-Proto` from loopback or `dashboard.trusted_proxies`; without it the session cookies would lack
`Secure`. Approved and applied in `/opt/data/config.yaml` (appended; file had no `dashboard:` section):

```yaml
dashboard:
  trusted_proxies:
    - "172.23.0.1"
```

Result: cookies `__Secure-hermes_session_{at,rt,provider}`, `Path=/agent; Secure; HttpOnly; SameSite=lax`.
If the Docker network is ever recreated with another subnet, update this IP (dashboard log prints
`Dashboard trusted proxies: …` at startup).

## Apply (as executed 2026-10-17)

1. Baseline: image `nousresearch/hermes-agent@sha256:36099926da316742423544e055d4734777105ffe6341873af5459b957d0c2919`,
   restart count 0, `hermes status` gateway running, model `anthropic/claude-sonnet-5-5`, provider Anthropic.
2. Backup: `scripts/backup/run-hermes-backup.sh` → run `20261017T071438Z-991233` (7 SQLite DBs integrity OK,
   NAS copy verified), then `hermes-verify-restore.sh` isolated restore verified.
   Extra copies (mode 600) in `/home/rocky/hermes-backups/manual/`: `config.yaml.20261017-183544`,
   `dashboard-production.env.<ts>`. Caddy: `/root/caddy-backups/hermes-website.caddy.20261017-141800` and
   `Caddyfile.20261017-141800` (outside the `conf.d/*.caddy` import glob).
3. Appended `dashboard.trusted_proxies` (above) to `/opt/data/config.yaml` as user `hermes`.
4. Appended `HERMES_DASHBOARD_PUBLIC_URL=https://hermes.kcb.vn/agent` to `deploy/rocky/dashboard-production.env` (not in Git).
5. Recreated once: `docker compose -f deploy/rocky/compose.yaml -f deploy/rocky/compose.dashboard-production.yaml up -d --no-deps hermes`
   (18:36:24–18:36:30 +07). Same image digest; restart count 0; gateway and model unchanged.
6. Installed `deploy/rocky/caddy/hermes-website.caddy.example` (minus header comments) as
   `/etc/caddy/conf.d/hermes-website.caddy`; `caddy validate --config /etc/caddy/Caddyfile` → valid;
   `systemctl reload caddy` (PID 1065 unchanged, NRestarts 0). Caddy was not restarted.

## Verification results (2026-10-17)

`sh scripts/agent-path-smoke.sh https://hermes.kcb.vn 100.110.57.61` → 24/24 PASS.
`python3 -I scripts/agent-auth-acceptance.py deploy/rocky/dashboard-production.env 100.110.57.61` → 21/21 PASS.
Both were run on Rocky through its own tailnet IP (`curl --resolve` / patched resolver).

- [x] Public DNS path: `/agent/`, `/agent/login`, `/agent/api/*`, WS `/agent/api/pty` → 403 (Caddy).
- [x] Caddy access log: NAT `10.11.1.213` → only 403 under `/agent/*`; tailnet `100.x` → proxied.
      Cookie headers appear as `REDACTED` in logs.
- [x] Login page with fonts under `/agent/fonts/…`; login (basic provider) 200; `/agent/api/auth/me` 200.
- [x] `index.html` has `__HERMES_BASE_PATH__`; 16 JS/CSS assets all under `/agent/`, all 200.
- [x] Refresh on sub-routes `/agent/sessions`, `/agent/config`, `/agent/chat` → 200 (SPA served).
- [x] Cookies `__Secure-…; Path=/agent; Secure; HttpOnly; SameSite=lax`. The Platform sets no cookies.
- [x] WebSockets with single-use ticket: `/agent/api/pty` (binary data), `/agent/api/ws`, `/agent/api/console` → 101 + data.
- [x] WebSockets with session cookie only → 403 (ticket required); unauthenticated → 403.
      `/agent/api/display/ws` completes the handshake then closes `4401` without a display ticket (upstream design).
- [x] Unauthenticated API (`config`, `sessions`, `env`, `logs`) → 401. Logout 302, API afterwards 401.
- [x] Root `/login`, `/api/status`, `/api/config`, `/api/display/ws` → Platform 404 (no admin at root).
- [x] `/` byte-identical to the pre-change baseline (sha256); `POST /api/public/chat` `{}` → 400 as before
      and a real question → 200. `dm.kcb.vn` 200, `fleet.kcb.vn` 302, `bot.kcb.vn` 302 (same as before).
- [x] `ss -ltn` shows `127.0.0.1:19119` only.
- [x] Live inference after recreate: `hermes chat -Q -q …` answered; model/provider unchanged.
- [ ] **Not verified:** a real browser on an operator device (hosts override, DevTools 404 check,
      interactive pages, chat UI). Do this once from a Mac on the tailnet.

Upstream behaviour worth knowing (not a deployment defect):

- `/api/status` (and others in `dashboard_auth/public_paths.py`, e.g. `/api/health`, `/api/model/info`)
  are public by design (liveness probe). They are only reachable from the tailnet.
- In gated mode the WebSocket Host/Origin guard does not reject foreign `Origin`s; the single-use ticket
  (minted by an authenticated `POST /api/auth/ws-ticket`, unreadable cross-origin) is the boundary.

## Rollback

1. Caddy: `sudo cp -a /root/caddy-backups/hermes-website.caddy.20261017-141800 /etc/caddy/conf.d/hermes-website.caddy`,
   `sudo caddy validate --config /etc/caddy/Caddyfile`, `sudo systemctl reload caddy` (never restart).
   This alone removes `/agent` from the internet-facing host.
2. Only if the dashboard settings must also be undone: remove the `HERMES_DASHBOARD_PUBLIC_URL` line from
   `deploy/rocky/dashboard-production.env`, restore `/opt/data/config.yaml` from
   `/home/rocky/hermes-backups/manual/config.yaml.20261017-183544` (or delete the appended `dashboard:` block),
   then re-run the compose command in step 5 (second brief gateway interruption; needs approval).
   No `down`, no `down -v`, no volume pruning.
3. Re-run `sh scripts/agent-path-smoke.sh` (after step 1 expect `/agent` → Platform 404) and confirm `/`,
   `/api/public/chat` and the other sites.

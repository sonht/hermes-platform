# Hermes Platform — Rocky Linux deployment runbook

Status: observed deployment through P2.20, 2026-10-16. Working branch: `feat/production-foundation`. Production readiness is **not yet established**.

## Scope and safety

This server hosts other production healthcare applications. Operate **only** on the `hermes-platform` Compose project and `hermes-platform-agent` container. Never use host-wide `docker compose down`, `docker system prune`, or restart Docker/Caddy without separate review. No public port is published, no host Docker socket is mounted, and data resides in named volume `hermes-platform_hermes_data`. Do not commit secrets or real `.env` files.

## Repository and pinned image

- Repository: `sonht/hermes-platform`
- Deployment file: `deploy/rocky/compose.yaml`
- Rocky checkout: `/home/rocky/hermes-platform`
- Image: `nousresearch/hermes-agent@sha256:36099926da316742423544e055d4734777105ffe6341873af5459b957d0c2919` (pin must be updated only through reviewed change)
- Volume mounted at `/opt/data`; runtime config: `/opt/data/config.yaml`; runtime secrets: `/opt/data/.env`.
- Docker Compose: project `hermes-platform`, service `hermes`, container `hermes-platform-agent`.

## Confirmed deployment procedure

On Rocky, from the repository checkout:

```bash
cd /home/rocky/hermes-platform
git pull --ff-only origin feat/production-foundation
docker compose -f deploy/rocky/compose.yaml config -q
docker compose -f deploy/rocky/compose.yaml up -d --force-recreate --no-deps hermes
sleep 30
docker inspect hermes-platform-agent --format 'State={{.State.Status}} RestartCount={{.RestartCount}} ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}'
docker logs --tail 80 hermes-platform-agent
docker top hermes-platform-agent
```

The supported foreground gateway command is configured in Compose as `command: ["gateway", "run"]`. The image uses s6-overlay, so `init: false` is intentional and the upstream entrypoint must not be overridden in production. s6 supervises gateway-default and optional dashboard services. The `dashboard` supervisor existing is **not proof** that an HTTP dashboard is enabled.

## Troubleshooting history and decisions

1. Initial `cap_drop: [ALL]` with `no-new-privileges:true` caused s6 errors (`s6-applyuidgid`, chown and supervise permission failures). Adding `CHOWN`, `SETUID`, `SETGID` in `compose.compat.yaml` was insufficient.
2. Commit `50e1f02` removed blanket `cap_drop: ALL`, returning to standard Docker capability defaults. Do not reapply compatibility overlay; it is superseded and should be removed in a separate reviewed cleanup.
3. Default CLI launch exited normally (`ExitCode=0`) and restarted under `unless-stopped`. `hermes gateway --help` explicitly described `gateway run` as recommended foreground mode for Docker.
4. Commit `5962f42` added `command: ["gateway", "run"]`.
5. P2.18 showed `running`, `RestartCount=0`, `OOMKilled=false`, and actual `gateway run --replace` under s6 supervision after 30 seconds.
6. P2.19/P2.20 confirmed `Gateway: running`, `Platforms: api_server`, `Providers: none connected`, model initially `anthropic/claude-opus-4.6`, and config paths above.
7. Nous Portal missing-credential warnings were observed. They do not demonstrate Anthropic API failure; no successful model invocation has yet been captured.

## Observability

```bash
docker ps --filter name=hermes-platform-agent
docker inspect hermes-platform-agent --format 'State={{.State.Status}} RestartCount={{.RestartCount}} OOMKilled={{.State.OOMKilled}}'
docker logs --tail 80 hermes-platform-agent
docker exec -u 10000 hermes-platform-agent hermes status
docker exec -u 10000 hermes-platform-agent hermes config check
```

Do not paste full `/opt/data/.env`, API keys, bearer tokens, or unredacted authentication output into issues, chat, or CI logs.

## Not yet completed

- Verify Anthropic authentication with a successful, billed, low-cost model call.
- Confirm model identifiers and entitlement against live Anthropic model catalog; do not assume every configured ID exists.
- Confirm gateway/API server access controls and dashboard functionality before publishing ports or DNS.
- Add healthcheck that tests service readiness, not just container `running`.
- Implement tested encrypted backup/restore of Hermes data to NAS, with secret-handling and rollback.
- Add CI validation, update policy for pinned image digest, staged release and rollback.
- Review repository visibility and secret exposure before production rollout.

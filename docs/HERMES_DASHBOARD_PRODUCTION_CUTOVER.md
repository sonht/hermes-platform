# P2.2 — Dashboard co-located with production Gateway

**Status: Prepared in GitHub; NOT deployed. Explicit operator approval required before production recreation.**

## Rationale

Upstream Hermes v0.22.2 bundles the React UI, FastAPI server and an s6-supervised dashboard service. The existing gateway container has `/run/service/dashboard` but `HERMES_DASHBOARD` is unset. An opt-in Compose override enables the upstream service **in the same container**, avoiding concurrent writers to the production volume across two containers.

Do not modify the production base Compose for this experiment. The override preserves its pinned image, gateway command, volume, resource limits and security options, while adding dashboard environment variables and a loopback-only host port.

## Security prerequisites

1. Review upstream Basic Auth behavior and test unauthenticated API/WebSocket access, not just the `302 /login` redirect. The isolated test proved interactive login, not a complete security audit.
2. Do not expose this administration surface via Caddy, DNS or a public interface, except the controlled `/agent` path described in `HERMES_AGENT_PATH_ROUTING.md`.
3. Use unique production admin credentials, a strong password/hash and a unique persistent signing secret; do not reuse test credentials.
4. Verify current volume backup and recovery procedure; do not dump secrets into terminal logs, chat, CI or GitHub.
5. Schedule a short maintenance window: **Compose service recreation interrupts the gateway**.
6. Record the original image, container restart count and gateway health.

## Preparation — does not deploy

On Rocky:

```sh
cd /home/rocky/hermes-platform
git status --short
git pull --ff-only origin feat/production-foundation
cp deploy/rocky/dashboard-production.env.example deploy/rocky/dashboard-production.env
chmod 600 deploy/rocky/dashboard-production.env
openssl rand -hex 32
# Edit dashboard-production.env locally. Never paste it.
sh scripts/dashboard-production-preflight.sh
```

The production env file must contain username, either password hash or password, and a 64-character-or-longer session signing secret. Check `git check-ignore deploy/rocky/dashboard-production.env`. The preflight intentionally fails while the test container still exists.

## Proposed cutover — NOT AUTHORIZED BY THIS DOCUMENT

Only after an explicit go/no-go decision, confirmed backup and rollback plan:

1. Record baseline `docker inspect` and `hermes status` (do not export env or secrets).
2. Stop the test dashboard project **without removing its volume**: `docker compose -f deploy/rocky/compose.dashboard-test.yaml down`.
3. Run the production preflight again; verify port 19119 is free.
4. Review the merged Compose configuration **locally** without sharing it (may contain expanded secrets): `docker compose -f deploy/rocky/compose.yaml -f deploy/rocky/compose.dashboard-production.yaml config`.
5. Operator-approved deployment command: `docker compose -f deploy/rocky/compose.yaml -f deploy/rocky/compose.dashboard-production.yaml up -d --no-deps hermes`. This **recreates the production container**; never run it as a diagnostic.
6. Verify `hermes status`, gateway model/provider, dashboard login, loopback bind, authenticated and unauthenticated API/WS behavior, and inference.
7. Verify other Rocky services remain healthy.

## Rollback — requires explicit operator approval

After collecting logs and recording failure, return to base Compose **without** the override:

```sh
docker compose -f deploy/rocky/compose.yaml up -d --no-deps hermes
```

This also recreates the production container and causes a second interruption. Confirm gateway model/provider and live inference afterward. Do **not** run `down -v`, prune volumes, change Docker daemon, or restart other services.

If the test dashboard must be restored, do so only after the production dashboard is no longer binding 19119, and with the isolated test Compose. No shared volume writes.

## Acceptance criteria

- Gateway and dashboard supervised in the same container; no second writer to production volume.
- Model/provider still Anthropic / `anthropic/claude-sonnet-5-5`.
- Login works and unauthenticated admin API and WebSocket calls fail.
- Dashboard accessible from Mac only via SSH tunnel to Rocky 127.0.0.1:19119.
- Production volume and other Rocky applications unchanged.
- Rollback validated and documented.

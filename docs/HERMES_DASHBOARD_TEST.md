# Hermes Dashboard — isolated test deployment (P1.2)

**Status:** configuration committed; **not deployed or security-approved**.

## Scope and guardrails

Use the pinned Hermes v0.22.2 image in a **separate Compose project**, dedicated Docker volume and network, and host loopback port 19119. The production gateway container, production volume `hermes-platform_hermes_data`, Caddy, DNS, and other applications must remain untouched. Do **not** combine the test Compose file with the production Compose file. The dashboard is an administrative surface capable of changing credentials/configuration.

The upstream image already includes `hermes_cli/web_dist/index.html`. Its FastAPI server supports dashboard Basic Auth, but login enforcement and Docker command semantics **have not yet been validated live**. The test intentionally has no production credentials or data, so production sessions will not appear.

## Prepare (no deployment yet)

On Rocky in `/home/rocky/hermes-platform`:

```sh
cp deploy/rocky/dashboard-test.env.example deploy/rocky/dashboard-test.env
chmod 600 deploy/rocky/dashboard-test.env
openssl rand -hex 32
```

Edit `dashboard-test.env` locally (never paste its contents into chat or GitHub). Set a unique username, a strong temporary password **or** the upstream-compatible password hash, and put the random 64-character hexadecimal string into `HERMES_DASHBOARD_BASIC_AUTH_SECRET`. Do not reuse Anthropic credentials. The test file is excluded by .gitignore only after the ignore rule is committed/verified; verify with `git check-ignore deploy/rocky/dashboard-test.env` before creating it.

Run the read-only preflight:

```sh
sh scripts/dashboard-test-preflight.sh
```

## Controlled test deployment — requires explicit approval

Only after reviewing the Compose and the preflight result:

```sh
docker compose -f deploy/rocky/compose.dashboard-test.yaml up -d
docker compose -f deploy/rocky/compose.dashboard-test.yaml ps
sh scripts/dashboard-test-smoke.sh
```

**Do not assume a successful HTTP 200 proves authentication.** Confirm unauthenticated requests cannot access sensitive `/api` routes or WebSocket methods, and validate login/logout before using the dashboard with real data. If the image's entrypoint does not support the standalone dashboard command, stop the test and investigate; do not alter production.

## Access from Mac

From the Mac (SSH access to Rocky required):

```sh
ssh -N -L 19119:127.0.0.1:19119 rocky@10.11.1.19
```

Then open `http://127.0.0.1:19119` in a Mac browser. The SSH destination is an example from the existing Rocky setup; use the reachable VPN/SSH endpoint.

## Stop and rollback

```sh
docker compose -f deploy/rocky/compose.dashboard-test.yaml down
```

This leaves the **test-only** volume for forensic inspection. Remove it separately **only after explicit approval and verification that no data is needed**. Never run `down -v`, `docker volume prune`, or production Compose operations as part of this test.

## Acceptance criteria

- Production container remains running with unchanged restart count.
- Test service alone binds host `127.0.0.1:19119`.
- No public host port, Caddy/DNS change, production mounts, or Docker socket.
- Valid Basic Auth; unauthenticated API/WebSocket access rejected; login/logout tested.
- Dashboard accessible over SSH tunnel from Mac.
- Test container can be removed without impacting production.

## Risks / next investigation

The s6 dashboard service is normally activated by `HERMES_DASHBOARD=1` alongside the Docker supervisor. This experiment instead invokes the dashboard CLI as the image command to avoid running an extra gateway; **verify image entrypoint behavior in the isolated test**. Docker host port binding alone does not guarantee isolation from local host users or other Docker peers. Use test-only credentials, avoid exposing the admin UI to untrusted networks, and review upstream auth implementation before connecting production state.

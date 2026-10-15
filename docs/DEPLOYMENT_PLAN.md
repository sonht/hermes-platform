# Hermes Platform — production rollout

## Verified infrastructure (2026-10-16)

- Rocky 9.5 x86_64; Docker 29.7.2; Compose v5.5.0.
- 62 GiB RAM, ~39 GiB available; ~83 GiB disk free.
- Caddy active at `/etc/caddy/Caddyfile`, ports 80/443.
- Proposed loopback port 18100 appeared unused at inspection time.
- `hermes.kcb.vn` did not resolve at inspection time.
- Existing NMPRP, VNTS, EMR, MSA, ICD-10 and V-DRG services must remain untouched.

## Delivery stages

1. Verify upstream NousResearch/hermes-agent release, license, image/build method, API/CLI capabilities and security implications. Pin a reviewed version or commit.
2. Build isolated, non-root Hermes runtime with restricted volumes, CPU/memory and no Docker socket. Never mount host SSH keys.
3. Implement authenticated web gateway only for supported Hermes interfaces; do not assume upstream has a multi-user web API.
4. Integrate Anthropic credentials via server-only secret management; never commit keys.
5. Add CI: dependency/security checks, tests, compose validation, container health and secret scanning.
6. Deploy to Rocky behind loopback, verify health and rollback; only then configure DNS/Caddy and expose authenticated HTTPS.
7. Implement terminology agents with read-only SNOMED/VNTS integration and expert-approved publication.

## Hard stops

- No public access before login/session security, authorization, CSRF and rate limits are validated.
- No autonomous changes to canonical RF2, refsets or production databases.
- No `docker system prune`, shared network changes, service restarts or global Caddy edits without impact review.
- No merge or production deploy without explicit user approval.

## Current status

Planning documents only. No containers, API integration or public domain configured.

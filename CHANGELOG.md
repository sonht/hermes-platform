# Changelog

All notable changes to Hermes Platform will be documented here.

Format follows Keep a Changelog; versions follow Semantic Versioning.

## [Unreleased]

### Added
- Read-only NMPRP API client for Hermes pilot (allowlist, CPT-code stripping, offline tests) and access runbook (`docs/NMPRP_HERMES_API_ACCESS.md`). Not connected to dm.kcb.vn yet.
- Knowledge layer for the NMPRP Hermes profile, not installed on Rocky: `SOUL.md`, `AGENTS.md`, memory seeds and four skills under `hermes/profiles/nmprp-mapping/`; project documents `docs/NMPRP_HERMES_BRAIN_DUMP.md` and `docs/NMPRP_HERMES_KIEN_TRUC.md` (architecture diagram, two-way feedback loop); originals kept in `docs/lich-su/`.
- Repository foundation and production rollout planning.
- Engineering versioning, change-management and backup/recovery policies.
- Hermes Agent Dashboard under `/agent` on hermes.kcb.vn via Caddy `X-Forwarded-Prefix`, Tailscale-only (deployed on Rocky 2026-10-17) — Caddy block, smoke and authenticated acceptance scripts, runbook with results and rollback.

No application release has been published yet.

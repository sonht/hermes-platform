# Changelog

All notable changes to Hermes Platform will be documented here.

Format follows Keep a Changelog; versions follow Semantic Versioning.

## [Unreleased]

### Added
- Read-only NMPRP API client for Hermes pilot (allowlist, CPT-code stripping, offline tests) and access runbook (`docs/NMPRP_HERMES_API_ACCESS.md`). Not connected to dm.kcb.vn yet.
- Repository foundation and production rollout planning.
- Engineering versioning, change-management and backup/recovery policies.
- Hermes Agent Dashboard under `/agent` on hermes.kcb.vn via Caddy `X-Forwarded-Prefix`, Tailscale-only (deployed on Rocky 2026-10-17) — Caddy block, smoke and authenticated acceptance scripts, runbook with results and rollback.

No application release has been published yet.

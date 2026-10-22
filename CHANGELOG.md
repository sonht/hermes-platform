# Changelog

All notable changes to Hermes Platform will be documented here.

Format follows Keep a Changelog; versions follow Semantic Versioning.

## [Unreleased]

### Added
- Five-skill documentation set (2026-10-23): official `hermes-agent` dependency guide, complete NMPRP skill references, review-change proposal template, installation/checksum/rollback runbook and source-pinned handoff. No production installation performed.
- Chat widget for dm.kcb.vn (`website/widget.js`, one `<script>` tag), a JSON knowledge base for login/registration (`knowledge/dm/`, drafts marked `chua-xac-minh`, generated from NMPRP `origin/main` by `scripts/build_knowledge.py`) and a 20-question golden set. Not deployed.
- Run runner `support/nmprp_may_chay.py` for the NMPRP «Hermes Agent» tab (polls NMPRP's run queue, runs the profile per batch, sends suggestions and per-PL2 results, pauses on call/token budget); `goi_hermes` takes optional model and reasoning level; client allowlist gains the six queue paths (`docs/NMPRP_HERMES_MAY_CHAY.md`). Not deployed; only simulated tests so far.
- Shadow run for one PL2 chapter (`support/nmprp_shadow.py`, run on the host as `python3 -m support.nmprp_shadow`): reads NMPRP (GET only), asks the `nmprp-mapping` profile through `hermes -z` (tool group `skills`, no terminal/web), validates every answer (branch key must exist in the frame, quotes must be verbatim, no CPT-like strings, max 3 per PL2) and writes local files. Never sends anything to NMPRP. Default is a dry run; token budget instead of dollars because Hermes reports no cost for this model.
- Profile `nmprp-mapping` installed on Rocky 2026-10-18 (empty profile via `hermes profile create`, knowledge files copied as user `hermes`, gateway stopped, no cron); verified steps recorded in `hermes/profiles/nmprp-mapping/README.md`.
- Read-only NMPRP API client for Hermes pilot (allowlist, CPT-code stripping, offline tests) and access runbook (`docs/NMPRP_HERMES_API_ACCESS.md`). Not connected to dm.kcb.vn yet.
- Knowledge layer for the NMPRP Hermes profile, not installed on Rocky: `SOUL.md`, `AGENTS.md`, memory seeds and four skills under `hermes/profiles/nmprp-mapping/`; project documents `docs/NMPRP_HERMES_BRAIN_DUMP.md` and `docs/NMPRP_HERMES_KIEN_TRUC.md` (architecture diagram, two-way feedback loop); originals kept in `docs/lich-su/`.
- Design (not implemented): Hermes Agent assisting NMPRP PL2/PL1 to CPT-node mapping — stage B orchestrator, stage C shadow pilot (`docs/NMPRP_HERMES_MAPPING_DESIGN.md`).
- Repository foundation and production rollout planning.
- Engineering versioning, change-management and backup/recovery policies.
- Hermes Agent Dashboard under `/agent` on hermes.kcb.vn via Caddy `X-Forwarded-Prefix`, Tailscale-only (deployed on Rocky 2026-10-17) — Caddy block, smoke and authenticated acceptance scripts, runbook with results and rollback.

### Changed
- Completed the four NMPRP skills against the M1 runner and current NMPRP API contracts: distinct model/API JSON, `CHO_XEM`, real reviewer feedback/cursors, independent-case learning, context-specific clinical semantics, QA denominators and human-controlled skill changes. Updated profile context and removed volatile counts from memory; runtime code and data are unchanged.
- `POST /api/public/chat` now checks the app and `Origin` (CORS), rate-limits per session/app/day instead of per IP, and answers from `knowledge/<app>/` instead of building a journey from the NMPRP source. Internal `POST /api/chat` is unchanged. Not deployed.

No application release has been published yet.

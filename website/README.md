# Hermes Website: public support MVP

The website sends questions to `POST /api/public/chat` with `{app, message, session}`. The endpoint answers **only** from reviewed entries in `knowledge/<app>/` (no Hermes/LLM call, no account access), checks the app and `Origin` against `website/apps.json`, and rate-limits per session, per app and per day (not per IP: all traffic reaches the server from 127.0.0.1 through Caddy). The public request body is capped at 8192 bytes (internal `/api/chat`: 4096).

Embed on a registered site: `<script src="https://hermes.kcb.vn/widget.js" data-app="dm" defer></script>`.

Add an app: add it to `website/apps.json` (exact origins, no wildcards), generate drafts with `scripts/build_knowledge.py`, have a person review and set `verification_status` to `da-duyet`, then deploy.

**Unverified entries.** Entries with `verification_status: "chua-xac-minh"` are still answered, always with a "chua duoc xac minh" notice. Do not deploy while `knowledge/dm/*.json` still contain unverified entries unless the project owner has explicitly accepted that.

**Not deployed.** The widget and the new `/api/public/chat` have not been deployed to Rocky.

**Behaviour change on the existing page `/`.** `website/app.js` sends no `session` and no `app`, so (a) all visitors of that page share one `anon` session bucket (5/min) and also spend the `dm` app quota (20/min, 500/day) shared with the widget; (b) off-topic questions now get the "no reviewed guidance" text; (c) browsers always send `Origin` on a POST, so opening the page locally at `http://127.0.0.1:8099` is rejected with 403. To try it locally, copy `website/apps.json`, add `http://127.0.0.1:8099` to the `dm` origins, and start the server with `HERMES_APPS_FILE=/path/to/that-copy.json`. Relative `knowledge` paths are always resolved from the repository root.

The rate limiter is in-memory and per process: restarting the service resets the daily counter.

The existing `POST /api/chat` remains Bearer-token protected for internal use. Do not expose that token to browsers or commit it to Git.

## Staging / deployment gate

1. Run `python3 -m compileall -q support website tests` and `python3 -m unittest discover -s tests -v`.
2. Verify the public endpoint cannot trigger CLI or Docker execution. Review the source and deployment environment.
3. Rate limits are per session/app/day (see `website/ratelimit.py`). Per-visitor IP limiting is impossible behind the NAT; keep the daily cap as the cost ceiling.
4. Require separate admin authentication before adding `/admin`. No admin interface is implemented in this PR.
5. After review, deploy via normal change control with rollback, then smoke-test: website 200, `/widget.js` 200, `POST /api/public/chat` 200 for a login question, foreign `Origin` 403, `{}` 400, internal chat without token 401 and no browser popup. Caddy must pass `OPTIONS` through to port 8099 (the default `reverse_proxy` block does).

Keep `NMPRP_SOURCE_PATH` read-only and local; do not allow user-selected paths or shell commands. Do not expose port 8099 to the Internet.

**Current status:** code review PR only; no Rocky deployment. Public answers come from the reviewed knowledge files for login and registration only, not general AI chat.

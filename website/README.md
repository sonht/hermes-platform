# Hermes Website: public support MVP

The website sends questions to `POST /api/public/chat` without a browser token prompt. This endpoint is deliberately restricted to login and registration guidance for dm.kcb.vn, using code-derived deterministic steps; it **never invokes the Hermes Agent**.

The existing `POST /api/chat` remains Bearer-token protected for internal use. Do not expose that token to browsers or commit it to Git.

## Staging / deployment gate

1. Run `python3 -m compileall -q support website tests` and `python3 -m unittest discover -s tests -v`.
2. Verify the public endpoint cannot trigger CLI or Docker execution. Review the source and deployment environment.
3. Review rate limiting: current in-memory limiter keys on the direct peer IP, so behind Caddy **all visitors share the same 5/min quota**. This is safe as a conservative preview but unsuitable for real public traffic. Configure a trusted proxy-aware rate limiter before production.
4. Require separate admin authentication before adding `/admin`. No admin interface is implemented in this PR.
5. After review, deploy via normal change control with rollback, then smoke-test website 200, public login guidance 200, internal chat without token 401 and no browser popup.

Keep `NMPRP_SOURCE_PATH` read-only and local; do not allow user-selected paths or shell commands. Do not expose port 8099 to the Internet.

**Current status:** code review PR only; no Rocky deployment. Public answers are limited to two topics, not general AI chat.

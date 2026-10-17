# Hermes Code-Aware Support V2.1 (safe staging)

## What this PR does
- Keeps existing public login/register responses.
- For other public questions, searches bounded allowlisted NMPRP source trees and returns **source file references only**.
- Does **not** send untrusted public messages to the Hermes CLI/agent.
- Does **not** give public users shell, SSH, repository write, DB, log or deployment permissions.
- Preserves the private Bearer-protected /api/chat endpoint.

## Important limitations
- File/line matches are **not verified user instructions**.
- Source references may expose internal paths. Review suitability for public display before production rollout.
- Search is per request and bounded, but not indexed; rate limiting currently uses Caddy peer address and is shared across users. Production requires trusted per-client rate limiting and capacity tests.
- A true public AI answerer requires a separately isolated inference service with **no tools**, strict timeouts, input/output filtering, quotas, evidence handling, and human security review. Do not simply set HERMES_AGENT_ENABLED for public requests.

## Review and deployment
1. Review changes and test the PR in CI.
2. Validate on Rocky with python3.11 -m unittest discover -s tests -v.
3. Review public source reference disclosure policy before merge.
4. Merge only after approval; deploy with a rollback plan. Do not alter backup scripts or unrelated services.

## Next milestone
Build offline redacted documentation/index from approved sources; run inference in a sandbox without tools; test prompt injection, secrets, concurrency and cost controls.

## Optional public inference (disabled by default)
- `HERMES_PUBLIC_AI_ENABLED=1` explicitly opts in to a **tool-free** HTTPS chat-completions API, not the Hermes CLI.
- Set `HERMES_PUBLIC_AI_URL`, `HERMES_PUBLIC_AI_MODEL`, `HERMES_PUBLIC_AI_KEY` via a protected service environment. Do not commit credentials.
- Current retrieval returns **file paths and line numbers only**, not code contents. Thus the AI must **not invent detailed instructions**. This is a scaffolding milestone, not a full code-understanding bot.
- Before enabling for the public, implement a redacted and approved documentation index, API host allowlist, per-user quota at Caddy/edge, billing limits, and security review.
- The existing five-requests-per-minute shared limiter remains a limitation. Keep inference disabled on production until resolved.

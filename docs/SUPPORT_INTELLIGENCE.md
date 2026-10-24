# Hermes Support Intelligence — H05

## Scope
Collect privacy-minimized, structured feedback for multiple Rocky-hosted applications. Produce reviewable proposals for FAQs, usability improvements, bugs, feature requests and AI answer quality. No automatic publication or production code changes.

## Data contract
`app`: registered application slug (e.g. nmprp, icd10, fleet).
`kind`: faq | ux | bug | feature | ai_quality.
`summary`: short sanitized description (max 600 characters).
`day`: UTC date; `status`: new/reviewed/resolved (future workflow).
No raw chat transcripts, IPs, access tokens, user identifiers, screenshots or patient information are intended for storage.

**Warning:** Regex-based sanitization is not a sufficient de-identification mechanism for production healthcare data. The current module is an offline prototype, not a public intake API. Before collecting real user feedback, add consent/notice, DLP/PII checks, app allowlist, access control, abuse controls, encryption/backup, deletion/export policy, and security review.

## Pipeline
1. Widget displays notice and an explicit feedback action (not silent transcript capture).
2. Server validates application identity, kind and size; rate limits at trusted edge.
3. Redact/normalize and persist only reviewed/minimized summaries.
4. Cluster near-duplicates by semantic similarity and human-verified issue identity.
5. Dashboard shows counts and trends by application and category, with drilldown available only to authorized admins.
6. FAQ candidates require editorial approval before publishing to Knowledge Engine.
7. Bug and feature candidates require triage before creating/updating GitHub Issues.
8. Developer Agent works in branch/PR with CI; production merge/deploy requires human approval.
9. Compare issue rates before and after releases, with denominator (sessions/active users) and confidence.

## Safety boundaries
- Public widget cannot read analytics, source code, logs, database or GitHub.
- Internal aggregation runs as an authenticated administrative job, not a public API.
- Do not count repeated spam as distinct user requests; maintain aggregate counts and de-duplicate with privacy-preserving methods.
- Do not auto-label a report as a confirmed bug.
- No auto-created GitHub Issues until explicit admin approval and PII scrub.
- Default retention target: 30 days for minimized individual reports; aggregated counts may follow an approved separate policy.

## Current implementation
`support/intelligence.py` provides SQLite schema, basic redaction, aggregate counts and a callable retention routine. It is wired into `website/server.py` only as the opt-in `POST /api/public/feedback` (off unless `HERMES_FEEDBACK_ENABLED=1`; needs a registered app listed in `HERMES_FEEDBACK_APPS`, an allowed origin and passes the rate limiter) and the admin-only dashboard routes. When enabled it stores minimized, redacted reports (identical app + kind + text on the same day count once). A production deployment requires an explicit retention scheduler and hardened intake service.

## Delivery stages
H05-A: schema, tests, admin-only offline aggregates.
H05-B: consent-based intake API with edge anti-abuse, reviewed redaction and authenticated admin.
H05-C: clustering, FAQ Studio, UX/Bug/Feature boards, GitHub issue proposals.
H05-D: trends, support friction score, release impact and weekly reports.

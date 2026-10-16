# DM.KCB.VN Code-Aware Support — Phase 1

Status: design + verified source inventory, **not deployed**. Branch: `feat/dm-code-aware-support`.

## Objective
Build a Zalo OA support assistant that derives user guidance from the **deployed** NMPRP implementation, rather than relying on hand-written FAQs. Hermes handles analysis and answering; NMPRP remains the authoritative application. Do not give the assistant write access to NMPRP or user accounts.

## Verified source inventory (NMPRP main, inspected 2026-10-17)
- `README.md`: production at `dm.kcb.vn`, React/Vite frontend, FastAPI backend, PostgreSQL; production version must be checked through `GET /health`, not README.
- `frontend/src/AuthAdmin.jsx`: account login/admin UI; Google credential integration, role-based controls, and API calls to `/admin/auth`.
- `frontend/src/HelpGuide.jsx`: in-app help tab, embeds two Markdown guides.
- `frontend/src/guides/anh_xa_pl3_icd9.md` and `anh_xa_pl3_cpt.md`: existing user guidance.
- `frontend/src/HelpDot.jsx`: inline help strings for operational controls.
- `backend/app/tests/test_google_login.py`: Google login checks; unknown/unverified emails rejected; pre-registered email allowed. These are **test expectations**, not confirmation of deployed UI behavior.

## Workflow
1. **Repository inventory**: read frontend routes, visible labels, forms, help text, backend API handlers, authorization, tests. Record exact repo commit SHA.
2. **Journey extraction**: emit versioned structured records: `intent`, `role`, `prerequisites`, `steps`, `failure_modes`, `source_paths`, `source_commit`, `verification_status`.
3. **Production verification**: check deployed `/health` and read-only UI/browser tests with a nonprivileged test account. Never assume main branch equals deployed commit. Unverified instructions must be labeled as such.
4. **Knowledge publication**: index only reviewed/verified journeys; redact secrets, tokens, personal data, admin-only operational details.
5. **Runtime**: Zalo OA webhook -> isolated gateway (signature verification, dedupe, rate limit) -> retrieval by intent/role/version -> Hermes answer with concise actionable steps -> Zalo OA send API.
6. **Escalation**: if source is missing, conflicting, outdated, or the user reports a novel error, ask for the exact error text (without secrets), or route to human support.
7. **Update**: on NMPRP release, diff affected source files, regenerate impacted journeys, rerun tests, approve and publish. Do not auto-publish on every push.

## First vertical slice: account sign-in
Intent: “Hướng dẫn tôi đăng nhập dm.kcb.vn”.
Sources to inspect next: `AuthAdmin.jsx`, `DangKyGmail.jsx`, `DangKyChuyenGia.jsx`, `GoogleCredentialButton.jsx`, `backend/app/api/auth_admin.py`, `backend/app/tests/test_google_login.py`.
Expected assistant behavior: distinguish Google sign-in, non-Google accounts, registration pending approval, and common errors, but only after UI validation. Never ask for passwords, OTP, or access tokens.

## MVP acceptance
- At least 20 real login/registration questions with expected, reviewed answers.
- Every operational claim has a source path/commit and deployment verification status.
- No invented button names or navigation steps; refuse/escalate uncertain instructions.
- No repository credentials or PII in the knowledge index, prompts, or logs.
- Zalo integration behind feature flag; no publicly exposed webhook until OA app configuration and signature verification are tested.
- Production NMPRP and Hermes containers untouched until isolated tests pass.

## Next implementation tasks
1. Implement a **read-only** repository scanner and structured journey JSON generator, with source references.
2. Create 20-item sign-in golden test set and CLI evaluator; compare outputs to source and current UI.
3. Add Hermes adapter for retrieved journeys (read-only tools, schema-constrained responses).
4. Add Zalo gateway separately with webhook verification, idempotency, message queue, and human escalation.
5. Stage locally; create PR for review. **No automatic merge/deploy**.

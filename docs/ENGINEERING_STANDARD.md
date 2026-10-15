# Hermes Platform — Engineering Standard

Status: proposed standard (not yet enforced). Owner: sonht.

## Product and environments
GitHub is the canonical source; Mac Pro and Mac Mini are developer clients; Rocky Linux is the production host. Automated CI checks run on pull requests; no separate manual staging environment is required. Production rollout uses a gated deployment and immediate post-deploy smoke tests. Never disturb other Rocky applications.

## Versioning
Use Semantic Versioning MAJOR.MINOR.PATCH for Hermes Platform, independent of the upstream Hermes Agent version. Before v1.0.0, breaking changes may occur in minor releases and must be documented. Use annotated tags v0.1.0, v0.1.1, etc. Record upstream Hermes image digest, app commit SHA, schema migration version and deployed time in each release manifest. Never deploy mutable image tags without pinning their digest.

## Branch and review
main is protected and releasable; feature/fix/docs branches use pull requests. Require CI, security checks, code review and explicit approval before merge or production deploy. No force push to main. Keep a HANDOFF.md for agent context and unfinished work.

## Change history
Every user-visible change appears in CHANGELOG.md under Added/Changed/Fixed/Security/Deprecated/Removed. Each release has GitHub Release notes, linked issues/PRs, upgrade steps, breaking changes, migration instructions, rollback instructions and test evidence.

## CI/CD gates
Run lint, type checks, unit/integration tests, container build, Docker Compose config validation, dependency and container vulnerability scanning, secret scanning, SBOM generation, migration compatibility checks. Build once; deploy the exact immutable artifact. Prevent overlapping deployments.

## Deployment and rollback
Production is Rocky. Before any release, take verified backups, record the currently deployed image digest and database schema version. Perform health/readiness checks and a representative Hermes-Claude request with cost controls. On failure, roll back the application artifact; database downgrade is NOT assumed safe. Prefer backward-compatible expand/contract migrations and point-in-time database restore when required.

## Security
Hermes runtime must not receive the host Docker socket, SSH private keys or privileged container mode. Separate database credentials and least-privilege network access. Never commit API keys. Authenticate and authorize web access before exposing it publicly; HTTPS, CSRF defenses, rate limits, audit logs and request limits are required. Terminology publication always requires human approval.

## Operational observability
Expose authenticated health/readiness endpoints, structured logs with request IDs, deployment version endpoint (no secrets), uptime/error/latency metrics, alerting on backup failure and critical service failure. Define retention and redact clinical or sensitive data from logs.

## Release acceptance
Release is complete only when CI passes, rollback path is documented, backup is verified, smoke tests pass and deployment manifest/changelog are updated.

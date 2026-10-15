# Hermes Platform

Production-oriented, self-hosted Hermes Agent integration for healthcare terminology workflows.

## Environments

- GitHub: source of truth and reviewed changes.
- Mac Pro / Mac Mini: development clients.
- Rocky Linux: production deployment target (`/home/rocky/hermes-platform`).

## Safety rules

- No secrets in Git; no host Docker socket in agent containers.
- No direct access to production terminology databases from autonomous agents.
- Deploy only after CI, review, explicit approval and rollback preparation.
- Public access requires authentication, HTTPS and bounded execution permissions.

## Status

Repository initialized. **Hermes is not installed or deployed yet.**

See `docs/DEPLOYMENT_PLAN.md` on the implementation branch for the rollout plan.

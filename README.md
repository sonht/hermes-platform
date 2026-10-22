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

The repository contains the Hermes deployment configuration, the NMPRP M1 host runner, and a reviewed-source skill profile. Repository content alone does not establish the version currently deployed on Rocky.

## NMPRP skills

- [Skill profile and five-skill index](hermes/profiles/nmprp-mapping/README.md).
- [Installation, verification and rollback](docs/NMPRP_HERMES_SKILLS_INSTALL.md).
- [Official hermes-agent skill: use, configuration, themes and orchestration](docs/HERMES_AGENT_SKILL.md).
- [Source versions, checks and handoff](docs/NMPRP_HERMES_SKILLS_RELEASE.md).

The new documents do not install a runtime, publish terminology or approve NMPRP suggestions. Production operation follows the deployment and owner approval procedures.

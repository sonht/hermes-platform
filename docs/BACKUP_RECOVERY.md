# Hermes Platform — Backup and Disaster Recovery Policy

Status: design policy; backup jobs are NOT yet installed or verified.

## Scope
Back up PostgreSQL application data, Hermes persistent state (sessions, skills, workflows and configuration as appropriate), user-uploaded documents, audit records, encrypted deployment configuration, and release manifests. Do not back up live database files by arbitrary file copy. Keep API secrets out of Git and plaintext archives.

## Storage and redundancy
Use the existing Rocky-to-Synology NAS backup infrastructure only after checking available capacity, ACLs, backup encryption and retention; do not modify current backup jobs. Apply 3-2-1 where feasible: working data, local restore copy, separate NAS copy, plus offsite/immutable copy if available. A single NAS is not sufficient disaster recovery.

## Proposed schedule (to confirm against actual workload)
- Database: nightly consistent backup; enable WAL archiving / PITR if recovery point objective requires it.
- Hermes state and uploads: daily versioned backup using a consistent snapshot or maintenance-safe procedure.
- Deployment manifests and encrypted configuration: each approved release.
- Retention: daily 14 days, weekly 8 weeks, monthly 6 months, subject to capacity and policy.
- Verify archive checksums and backup job exit codes on every run.
- Monthly restore drill into an isolated location without touching production.

## Recovery targets
Initial targets, to be validated after restore drills: RPO <= 24h for general platform state, RTO <= 4h for app recovery. For critical review/audit data, use stricter RPO with WAL/PITR and durable audit storage.

## Restore procedure
1. Declare incident, freeze writes and record current state.
2. Select backup and matching release manifest (app version, Hermes image digest, schema version).
3. Restore into an isolated target; verify integrity, migrations, permissions and secret injection.
4. Execute functional tests and validate audit continuity.
5. Switch traffic only with explicit approval; monitor and document outcome.

## Prohibitions
Never run destructive restore, prune, database reset or broad rsync deletion without explicit authorization. Never assume a successful backup means it can be restored.

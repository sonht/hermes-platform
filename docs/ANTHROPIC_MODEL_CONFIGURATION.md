# Hermes Platform — Anthropic Claude model configuration

Status: configuration steps observed on Rocky, 2026-10-16. **Configured model strings are not proof of Anthropic API availability.**

## Current runtime layout

- Hermes Docker container: `hermes-platform-agent`
- Data directory: `/opt/data` in named Docker volume
- Main config: `/opt/data/config.yaml`
- Secret environment file: `/opt/data/.env`
- Gateway is started with `hermes gateway run` under s6 supervision.
- Hermes CLI reported `Provider: Auto` and `Providers: none connected` before API key setup.
- User entered an Anthropic API key using a hidden terminal prompt and Hermes reported it was written to `/opt/data/.env`. **Do not infer key validity or provider connectivity from this message.**

## Model selection (observed)

The command `hermes config set model <value>` automatically redirects to `model.default` while preserving existing model subkeys.

Example:

```bash
docker exec -u 10000 hermes-platform-agent hermes config set model.default anthropic/claude-sonnet-5-5
docker exec -u 10000 hermes-platform-agent hermes config get model.default
docker exec -u 10000 hermes-platform-agent hermes status
```

The user **successfully wrote** `anthropic/claude-haiku-5-5` and later `anthropic/claude-sonnet-5-5` to `model.default`. The last observed choice was Sonnet 5.5.

Requested candidate values (must be checked against the provider's live supported model list before use):

| Display name | Hermes configuration string | Verification |
| --- | --- | --- |
| Haiku 5.5 | `anthropic/claude-haiku-5-5` | Config write observed; API availability unverified |
| Sonnet 5.5 | `anthropic/claude-sonnet-5-5` | Config write observed; API availability unverified |
| Opus 5.5 | `anthropic/claude-opus-5-5` | Proposed only; API availability unverified |

These are *requested strings*, **not an assertion that Anthropic has released or enabled these models**. A successful `config set` does not validate the model against the Anthropic API. Consult the official Anthropic model catalog and the account's available models; use an actual supported ID if different. The earlier configured `anthropic/claude-opus-4.6` was also observed.

For a one-off task, Hermes supports `-m MODEL` and `-z PROMPT`:

```bash
docker exec -u 10000 hermes-platform-agent hermes -m '<verified-model-id>' -z 'Reply with one short sentence.'
```

This sends a real API request, may incur cost, and requires valid credentials. A CLI request's successful answer plus model/provider evidence is needed for acceptance.

## Secrets: safe operation

Never commit an API key or `/opt/data/.env` to GitHub. Never paste credentials in chat or terminal commands. Keep `.env` readable only by the service user. The earlier operator workflow used an interactive hidden prompt (`stty -echo`) to append `ANTHROPIC_API_KEY` to `/opt/data/.env`; ensure any future secret editing restores terminal echo on interruption and does not log values. Do not run `cat /opt/data/.env` in shared sessions.

Check only whether the key entry exists (without printing it):

```bash
docker exec -u 10000 hermes-platform-agent sh -c 'if grep -q "^ANTHROPIC_API_KEY=" /opt/data/.env; then echo "ANTHROPIC_API_KEY: CONFIGURED"; else echo "ANTHROPIC_API_KEY: MISSING"; fi'
```

This only checks file contents, not whether the running gateway has reloaded them or whether Anthropic accepts the key. Validate via an authorized low-cost request. Do not assume that `hermes status` must change immediately after editing `.env`.

## Model-switching policy (proposed, not implemented)

- Manual selection per task: `-m` without changing global default.
- Default selection: `model.default` for new invocations.
- Future web UI: model picker with actual live-supported models, permission checks, cost guardrails and audit logs.
- Future multi-agent routing: Haiku for simple batch work, Sonnet for standard tasks, Opus for difficult reviews, **subject to availability, benchmark results and budget**.

## Acceptance checklist

1. `hermes config get model.default` returns intended value.
2. `hermes status` reports gateway running.
3. Anthropic key exists in protected `.env`, without exposure.
4. Confirm supported model IDs from authoritative Anthropic catalog.
5. Run an inexpensive real test and capture redacted success/error details.
6. Verify restart/persistence and that no secret appears in Git history or logs.

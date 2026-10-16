# Hermes Website - local Rocky staging only

Do not publish port 8099, change Caddy, merge or deploy production without approval.

On Rocky in a separate checkout of the feature branch:

```bash
git clone --branch feat/dm-code-aware-support https://github.com/sonht/hermes-platform.git /tmp/hermes-support-staging
cd /tmp/hermes-support-staging
python3 -m compileall -q support website tests
python3 -m unittest discover -s tests -v
```

The website runs on localhost only. To test against the existing container,
set `HERMES_GATEWAY_MODE=docker`, `HERMES_AGENT_ENABLED=1`, and a strong
`HERMES_WEB_TOKEN` **outside the repository**. Set `NMPRP_SOURCE_PATH` to
a read-only checkout of sonht/nmprp. The invoking account needs Docker access;
Docker access is effectively privileged, so use an isolated test account or
approved restricted gateway before any public exposure.

For local smoke test, with token set in the shell:

```bash
HERMES_WEB_TOKEN="$HERMES_WEB_TOKEN" HERMES_AGENT_ENABLED=1 HERMES_GATEWAY_MODE=docker NMPRP_SOURCE_PATH=/path/to/nmprp python3 website/server.py
```

In another terminal:

```bash
curl -fsS -H "Authorization: Bearer $HERMES_WEB_TOKEN" -H 'Content-Type: application/json' --data '{"message":"Hướng dẫn đăng nhập dm.kcb.vn"}' http://127.0.0.1:8099/api/chat
```

No deployment is performed by this document. The current Bearer-token UI is
suitable only for trusted local staging, not multi-user public access.

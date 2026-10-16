#!/bin/sh
set -eu
BASE="http://127.0.0.1:19119"
command -v curl >/dev/null 2>&1 || { echo "curl required" >&2; exit 1; }
code=$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' --max-time 8 "$BASE/" || true)
echo "Unauthenticated GET /: HTTP $code"
case "$code" in
  401|403|302|303|307|308) echo "Auth-gate candidate: inspect Location and login behavior manually." ;;
  200) echo "WARNING: HTTP 200 does not prove an auth bypass (could be login SPA). Verify API and WebSocket access before use." ;;
  *) echo "Unexpected response; inspect dashboard logs." ;;
esac
echo "Production gateway:"
docker inspect hermes-platform-agent --format 'Status={{.State.Status}} RestartCount={{.RestartCount}} OOMKilled={{.State.OOMKilled}}'
echo "Test dashboard:"
docker inspect hermes-dashboard-test --format 'Status={{.State.Status}} RestartCount={{.RestartCount}} OOMKilled={{.State.OOMKilled}}' 2>/dev/null || true
echo "This is a preliminary smoke test, NOT an authentication/security certification."

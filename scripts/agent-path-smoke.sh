#!/bin/sh
# Read-only smoke test for https://hermes.kcb.vn/agent. No credentials are used or printed.
# Usage: sh scripts/agent-path-smoke.sh [https://hermes.kcb.vn]
set -eu
BASE="${1:-https://hermes.kcb.vn}"
command -v curl >/dev/null 2>&1 || { echo "curl required" >&2; exit 1; }
rc=0
code() { curl -sS -o /dev/null -w '%{http_code}' --max-time 10 "$@" || echo 000; }
check() { # name expected-regex actual
  if printf '%s' "$3" | grep -Eq "^($2)$"; then echo "PASS: $1 -> $3"; else echo "FAIL: $1 -> $3 (expected $2)"; rc=1; fi
}
check "Platform root"              '200'           "$(code "$BASE/")"
check "/agent redirects to slash"  '308'           "$(code "$BASE/agent")"
check "/agent/ is gated (login)"   '302|303|307|200|401' "$(code "$BASE/agent/")"
loc=$(curl -sS -o /dev/null -D - --max-time 10 "$BASE/agent/" | tr -d '\r' | sed -n 's/^[Ll]ocation: //p')
case "$loc" in /agent/login*|"$BASE"/agent/login*) echo "PASS: login redirect keeps prefix ($loc)";; *) echo "FAIL: login redirect lost prefix: '$loc'"; rc=1;; esac
check "Unauth API gated"           '401|403|302|303|307' "$(code "$BASE/agent/api/status")"
check "Unauth WS refused"          '400|401|403|404|302' "$(code -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: c21va2UtdGVzdC1rZXk=' "$BASE/agent/api/display/ws")"
# Admin surface must not leak at the hostname root.
for p in /login /api/display/ws /api/status; do
  c=$(code "$BASE$p"); case "$c" in 404|301|302|307|308) echo "INFO: $p at root -> $c (verify it is Platform, not Dashboard)";; *) echo "WARN: $p at root -> $c";; esac
done
echo "Automated smoke only. Authenticated browser tests (login, refresh, WebSocket traffic) remain manual."
exit $rc

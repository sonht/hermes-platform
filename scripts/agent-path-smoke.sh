#!/bin/sh
# Read-only smoke test for https://hermes.kcb.vn/agent. No credentials are used or printed.
# Usage: sh scripts/agent-path-smoke.sh [https://hermes.kcb.vn] [TAILNET_IP]
#   Public DNS path: /agent/* must be 403 (Caddy tailnet-only rule).
#   TAILNET_IP (e.g. 100.110.57.61, Rocky's Tailscale IP): gated dashboard checks via curl --resolve.
set -eu
BASE="${1:-https://hermes.kcb.vn}"
TS_IP="${2:-}"
HOST=$(printf '%s' "$BASE" | sed -E 's#^https?://([^/:]+).*#\1#')
command -v curl >/dev/null 2>&1 || { echo "curl required" >&2; exit 1; }
rc=0
RESOLVE=""
code() { curl -sS -o /dev/null -w '%{http_code}' --max-time 10 $RESOLVE "$@" || echo 000; }
check() { # name expected-regex actual
  if printf '%s' "$3" | grep -Eq "^($2)$"; then echo "PASS: $1 -> $3"; else echo "FAIL: $1 -> $3 (expected $2)"; rc=1; fi
}
wscode() { code --http1.1 -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: c21va2UtdGVzdC1rZXkxNg==' "$@"; }

echo "== Public path (DNS)"
check "Platform root"               '200' "$(code "$BASE/")"
check "Public chat API (empty body)" '400' "$(code -X POST -H 'Content-Type: application/json' -d '{}' "$BASE/api/public/chat")"
check "/agent redirects to slash"   '308' "$(code "$BASE/agent")"
for p in /agent/ /agent/login /agent/api/status /agent/api/config; do
  check "public $p denied" '403' "$(code "$BASE$p")"
done
check "public WS /agent/api/pty denied" '403' "$(wscode "$BASE/agent/api/pty")"
# Admin surface must not leak at the hostname root (Platform answers 404).
for p in /login /api/display/ws /api/status /api/config; do
  check "root $p is Platform 404" '404' "$(code "$BASE$p")"
done

if [ -n "$TS_IP" ]; then
  echo "== Tailnet path ($TS_IP)"
  RESOLVE="--resolve $HOST:443:$TS_IP"
  check "/agent/ is gated (login)" '302' "$(code "$BASE/agent/")"
  loc=$(curl -sS -o /dev/null -D - --max-time 10 $RESOLVE "$BASE/agent/" | tr -d '\r' | sed -n 's/^[Ll]ocation: //p')
  case "$loc" in /agent/login*|"$BASE"/agent/login*) echo "PASS: login redirect keeps prefix ($loc)";; *) echo "FAIL: login redirect lost prefix: '$loc'"; rc=1;; esac
  check "login page" '200' "$(code "$BASE/agent/login")"
  check "login font under prefix" '200' "$(code "$BASE/agent/fonts/Collapse-Regular.woff2")"
  # /api/status is in upstream PUBLIC_API_PATHS (liveness probe): 200 without auth by design.
  check "Upstream public /agent/api/status" '200' "$(code "$BASE/agent/api/status")"
  for p in /agent/api/config /agent/api/sessions /agent/api/env /agent/api/logs; do
    check "Unauth $p" '401' "$(code "$BASE$p")"
  done
  for p in /agent/api/pty /agent/api/ws /agent/api/console; do
    check "Unauth WS $p" '401|403' "$(wscode "$BASE$p")"
  done
fi
echo "Automated smoke only. Authenticated checks: scripts/agent-auth-acceptance.py (no secrets printed); real browser: manual."
exit $rc

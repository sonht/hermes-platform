#!/bin/sh
# Read-only: no container restarts, no secrets printed.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
BASE=deploy/rocky/compose.yaml
OVERRIDE=deploy/rocky/compose.dashboard-production.yaml
ENV=deploy/rocky/dashboard-production.env
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
ok() { printf 'OK: %s\n' "$*"; }
command -v docker >/dev/null 2>&1 || fail "docker missing"
command -v ss >/dev/null 2>&1 || fail "ss missing"
test -f "$ENV" || fail "Create production auth env locally; do not paste it"
perm=$(stat -c %a "$ENV")
case "$perm" in 600|400) ;; *) fail "chmod 600 $ENV (current: $perm)" ;; esac
get() { sed -n "s/^$1=//p" "$ENV" | tail -n 1; }
test -n "$(get HERMES_DASHBOARD_BASIC_AUTH_USERNAME)" || fail "Username missing"
hash=$(get HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH)
pass=$(get HERMES_DASHBOARD_BASIC_AUTH_PASSWORD)
if test -n "$hash" && test -n "$pass"; then fail "Choose hash OR password"; fi
if test -z "$hash" && test -z "$pass"; then fail "Password/hash missing"; fi
secret=$(get HERMES_DASHBOARD_BASIC_AUTH_SECRET)
test ${#secret} -ge 64 || fail "Session signing secret too short"
test -z "$(docker ps -aq --filter name='^/hermes-dashboard-test$')" || fail "Test dashboard container exists; stop it before cutover (without -v)"
docker inspect hermes-platform-agent --format '{{.State.Running}}' 2>/dev/null | grep -qx true || fail "Production gateway not running"
if ss -lnt | grep -Eq '(^|[[:space:]])(127\.0\.0\.1|0\.0\.0\.0|\[::\]|\*):19119[[:space:]]'; then fail "Port 19119 occupied"; fi
docker compose -f "$BASE" -f "$OVERRIDE" config -q >/dev/null || fail "Merged Compose invalid"
ok "Production dashboard override validates; gateway remains untouched"
ok "Preflight is read-only. Requires explicit downtime approval and backup before apply."

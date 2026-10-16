#!/bin/sh
# Read-only checks; never print credentials.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
COMPOSE="$ROOT/deploy/rocky/compose.dashboard-test.yaml"
ENV="$ROOT/deploy/rocky/dashboard-test.env"
fail() { printf 'FAIL: %s\n' "$*" >&2; exit 1; }
ok() { printf 'OK: %s\n' "$*"; }
command -v docker >/dev/null 2>&1 || fail "Docker is missing"
command -v ss >/dev/null 2>&1 || fail "ss is missing"
test -f "$COMPOSE" || fail "Test compose file missing"
test -f "$ENV" || fail "Create deploy/rocky/dashboard-test.env first"
# Only plain KEY=value records are supported; no shell evaluation.
get_value() { sed -n "s/^$1=//p" "$ENV" | tail -n 1; }
user=$(get_value HERMES_DASHBOARD_BASIC_AUTH_USERNAME)
hash=$(get_value HERMES_DASHBOARD_BASIC_AUTH_PASSWORD_HASH)
pass=$(get_value HERMES_DASHBOARD_BASIC_AUTH_PASSWORD)
secret=$(get_value HERMES_DASHBOARD_BASIC_AUTH_SECRET)
test -n "$user" || fail "Basic Auth username missing"
test -n "$hash" || test -n "$pass" || fail "Basic Auth password/hash missing"
test ${#secret} -ge 64 || fail "Session signing secret must have at least 64 characters"
case "$(get_value HERMES_DASHBOARD)" in ""|0|false|FALSE) ;; *) fail "HERMES_DASHBOARD must not enable an extra s6 service" ;; esac
perm=$(stat -c %a "$ENV")
case "$perm" in 600|400) ;; *) fail "Set env file permissions to 600 (current: $perm)" ;; esac
if ss -lnt | grep -Eq '(^|[[:space:]])(127\.0\.0\.1|0\.0\.0\.0|\[::\]|\*):19119[[:space:]]'; then
  fail "Host port 19119 is already listening"
fi
test -z "$(docker ps -aq --filter name='^/hermes-dashboard-test$')" || fail "Test container already exists"
docker inspect hermes-platform-agent --format '{{.State.Running}}' 2>/dev/null | grep -qx true || fail "Production gateway is not running"
docker compose -f "$COMPOSE" config -q >/dev/null || fail "Compose validation failed"
ok "Auth configured, permissions restricted, port available, gateway running, Compose valid"
ok "No changes were made. Never paste dashboard-test.env or compose config output."

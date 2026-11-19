#!/usr/bin/env bash
# Restore a database dump into the SELECTED project's db container.
# Non-interactive by design: always verify CL_PROJECT before running.
# Always rehearse in cl-test first; never point this at production data.
set -euo pipefail

cd "$(dirname "$0")/.."
DUMP="${1:?usage: restore.sh <path-to-db-*.dump>}"
PROJECT="${CL_PROJECT:-cl-dev}"
OVERLAY="${CL_COMPOSE_OVERLAY:-deploy/compose.dev.yml}"

if [ ! -f "$DUMP" ]; then
  echo "dump not found: $DUMP" >&2
  exit 1
fi

# Verify the file that was actually passed in, not whatever path the sidecar
# happened to record (a dump may have been moved between backup and restore).
if [ -f "${DUMP}.sha256" ]; then
  EXPECTED="$(awk '{print $1}' "${DUMP}.sha256")"
  ACTUAL="$(sha256sum "$DUMP" | awk '{print $1}')"
  if [ -z "$EXPECTED" ] || [ "$EXPECTED" != "$ACTUAL" ]; then
    echo "checksum mismatch for $DUMP" >&2
    exit 1
  fi
  echo "checksum OK: $ACTUAL" >&2
else
  echo "WARNING: no checksum sidecar for $DUMP" >&2
fi

COMPOSE=(docker compose -p "$PROJECT" -f deploy/docker-compose.yml -f "$OVERLAY")
DB_USER="$("${COMPOSE[@]}" exec -T db printenv POSTGRES_USER)"
DB_NAME="$("${COMPOSE[@]}" exec -T db printenv POSTGRES_DB)"
if [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
  echo "cannot read POSTGRES_USER/POSTGRES_DB from the running container" >&2
  exit 1
fi

echo "Restoring into project: $PROJECT / database: $DB_NAME (ensure this is disposable/testing)" >&2

"${COMPOSE[@]}" exec -T db \
  pg_restore --clean --if-exists --no-owner \
  -U "$DB_USER" -d "$DB_NAME" < "$DUMP"

echo "restore finished; run migrations and integrity checks next"

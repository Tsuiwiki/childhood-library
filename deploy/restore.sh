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

if [ -f "${DUMP}.sha256" ]; then
  sha256sum -c "${DUMP}.sha256"
else
  echo "WARNING: no checksum sidecar for $DUMP" >&2
fi

echo "Restoring into project: $PROJECT (ensure this is a disposable/testing database)" >&2

docker compose -p "$PROJECT" -f deploy/docker-compose.yml -f "$OVERLAY" exec -T db \
  pg_restore --clean --if-exists --no-owner \
  -U "${POSTGRES_USER:?set POSTGRES_USER in .env}" \
  -d "${POSTGRES_DB:-childhood_library_dev}" < "$DUMP"

echo "restore finished; run migrations and integrity checks next"

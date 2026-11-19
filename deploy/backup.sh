#!/usr/bin/env bash
# Database + media backup. Run from any directory; paths resolve against the repo root.
# Requires a running db container and a repo-root .env (never committed).
set -euo pipefail

cd "$(dirname "$0")/.."
PROJECT="${CL_PROJECT:-cl-dev}"
OVERLAY="${CL_COMPOSE_OVERLAY:-deploy/compose.dev.yml}"
BACKUP_DIR="${BACKUP_ROOT:-./var/backups}"
MEDIA_DIR="${CL_MEDIA_ROOT:-./var/media}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${BACKUP_DIR}/db-${PROJECT}-${STAMP}.dump"

COMPOSE=(docker compose -p "$PROJECT" -f deploy/docker-compose.yml -f "$OVERLAY")

# Read credentials from the RUNNING container, not from the shell environment.
# Compose loads the repo-root .env for interpolation by itself; sourcing .env
# into bash would break on passwords containing shell metacharacters. Container
# values are authoritative, so base/overlay database names cannot drift apart.
DB_USER="$("${COMPOSE[@]}" exec -T db printenv POSTGRES_USER)"
DB_NAME="$("${COMPOSE[@]}" exec -T db printenv POSTGRES_DB)"
if [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
  echo "cannot read POSTGRES_USER/POSTGRES_DB from the running container" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

"${COMPOSE[@]}" exec -T db pg_dump -U "$DB_USER" -Fc "$DB_NAME" > "$OUT"

sha256sum "$OUT" > "${OUT}.sha256"
echo "backup written: $OUT (database: $DB_NAME)"
echo "checksum:       ${OUT}.sha256"

# Media backup is a separate, checksum-verified copy. Media files are only added,
# never removed by this script. Override CL_MEDIA_ROOT for cl-test drills.
if [ -d "$MEDIA_DIR" ]; then
  MEDIA_OUT="${BACKUP_DIR}/media-${PROJECT}-${STAMP}"
  mkdir -p "$MEDIA_OUT"
  rsync -a --checksum "$MEDIA_DIR/" "$MEDIA_OUT/"
  echo "media copy:     $MEDIA_OUT"
fi

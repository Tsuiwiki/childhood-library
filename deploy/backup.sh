#!/usr/bin/env bash
# Database backup. Run from any directory; paths are resolved relative to the repo root.
# Requires a running db container and a filled .env (never committed).
set -euo pipefail

cd "$(dirname "$0")/.."
PROJECT="${CL_PROJECT:-cl-dev}"
OVERLAY="${CL_COMPOSE_OVERLAY:-deploy/compose.dev.yml}"
BACKUP_DIR="${BACKUP_ROOT:-./var/backups}"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="${BACKUP_DIR}/db-${PROJECT}-${STAMP}.dump"

mkdir -p "$BACKUP_DIR"

docker compose -p "$PROJECT" -f deploy/docker-compose.yml -f "$OVERLAY" exec -T db \
  pg_dump -U "${POSTGRES_USER:?set POSTGRES_USER in .env}" -Fc \
  "${POSTGRES_DB:-childhood_library_dev}" > "$OUT"

sha256sum "$OUT" > "${OUT}.sha256"
echo "backup written: $OUT"
echo "checksum:       ${OUT}.sha256"

# Media backup is a separate, checksum-verified copy. Media files are only added,
# never removed by this script.
if [ -d "${MEDIA_ROOT:-./var/media}" ]; then
  MEDIA_OUT="${BACKUP_DIR}/media-${PROJECT}-${STAMP}"
  mkdir -p "$MEDIA_OUT"
  rsync -a --checksum "${MEDIA_ROOT:-./var/media}/" "$MEDIA_OUT/"
  echo "media copy:     $MEDIA_OUT"
fi

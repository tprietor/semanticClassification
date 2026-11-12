#!/usr/bin/env bash
# Respalda PostgreSQL del EC2 sin detener la API. Conserva siete días.
set -euo pipefail
umask 077

APP_DIR="${APP_DIR:-$HOME/semanticClassification}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/semantic-db-backups}"
mkdir -p "$BACKUP_DIR"
cd "$APP_DIR"

COMPOSE=(docker compose -f docker-compose.prod.yml --profile local-db)
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="$BACKUP_DIR/semantic_db_${stamp}.dump"
temporary="$(mktemp "$BACKUP_DIR/.semantic_db_${stamp}.XXXXXX")"
trap 'rm -f "$temporary"' EXIT

"${COMPOSE[@]}" exec -T db pg_dump -U sc_user -d semantic_db \
  --format=custom --no-owner --no-privileges > "$temporary"
"${COMPOSE[@]}" exec -T db pg_restore --file=/dev/null < "$temporary"
test -s "$temporary"
mv "$temporary" "$target"
trap - EXIT

find "$BACKUP_DIR" -maxdepth 1 -type f -name 'semantic_db_*.dump' \
  -mtime +7 -delete
echo "Respaldo verificado: $target ($(du -h "$target" | cut -f1))"

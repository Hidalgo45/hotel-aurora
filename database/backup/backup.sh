#!/usr/bin/env bash
# =============================================================================
#  Hotel Aurora - Respaldo de la base de datos (Linux / macOS / Git Bash)
#  Criterio 1.5 de la rubrica: estrategia basica de respaldo
#
#  Uso:  bash database/backup/backup.sh
# =============================================================================
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
set -a; source "$RAIZ/.env"; set +a

FECHA=$(date +%F)
DESTINO="$RAIZ/respaldos"
mkdir -p "$DESTINO"

export PGPASSWORD="$DB_PASSWORD"

echo "  Respaldando $DB_NAME..."

# 1. Respaldo completo, formato custom: comprimido y restaurable por tabla
pg_dump --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" \
        --dbname="$DB_NAME" --format=custom --compress=9 \
        --file="$DESTINO/aurora_$FECHA.dump"

# 2. Solo el esquema, para versionarlo junto al codigo
pg_dump --host="$DB_HOST" --port="$DB_PORT" --username="$DB_USER" \
        --dbname="$DB_NAME" --schema-only \
        --file="$DESTINO/esquema_$FECHA.sql"

unset PGPASSWORD

# 3. Retencion: 7 diarios. Los semanales y mensuales se archivan aparte.
find "$DESTINO" -name "aurora_*.dump" -mtime +7 -delete

echo "  Listo. Archivos en: $DESTINO"
ls -lh "$DESTINO"
echo
echo "  Recordatorio: un respaldo que nunca se restauro no cuenta como respaldo."
echo "  Ver database/backup/restore.md para la prueba de restauracion."

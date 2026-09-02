#!/bin/bash
# Backup script to dump the PostgreSQL database mapped dynamically in docker-compose
TIMESTAMP=$(date +"%F")
BACKUP_DIR="/backups"
DB_NAME="football_analytics"

mkdir -p "$BACKUP_DIR"

docker compose exec -T db pg_dump -U postgres "$DB_NAME" -F c > "$BACKUP_DIR/$DB_NAME-$TIMESTAMP.dump"
echo "Backup stored successfully at $BACKUP_DIR/$DB_NAME-$TIMESTAMP.dump"

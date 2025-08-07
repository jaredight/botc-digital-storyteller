#!/bin/bash
# Backup script for Blood on the Clocktower

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Creating backup: $DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
if [ "$ENVIRONMENT" = "production" ]; then
    docker-compose exec postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_DIR/database_$DATE.sql
else
    docker cp botc-backend:/app/src/database/app.db $BACKUP_DIR/database_$DATE.db
fi

# Backup configuration
cp .env $BACKUP_DIR/env_$DATE.backup

echo "Backup completed: $BACKUP_DIR"

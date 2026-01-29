#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"

# Validate required environment variables
for var in DB_HOST DB_DATABASE DB_USERNAME DB_PASSWORD; do
    if [ -z "${!var}" ]; then
        echo "Error: $var environment variable is not set" >&2
        exit 1
    fi
done

# Build connection string for psql
export PGHOST="$DB_HOST"
export PGDATABASE="$DB_DATABASE"
export PGUSER="$DB_USERNAME"
export PGPASSWORD="$DB_PASSWORD"

echo "Reinitializing database '$DB_DATABASE' on '$DB_HOST'..."

# Drop all objects in the database by dropping and recreating the public schema
# This is cleaner than DROP DATABASE for managed databases like Cloud SQL
echo "Dropping all objects in public schema..."
psql -c "DROP SCHEMA public CASCADE;"
psql -c "CREATE SCHEMA public;"
psql -c "GRANT ALL ON SCHEMA public TO $DB_USERNAME;"
psql -c "GRANT ALL ON SCHEMA public TO PUBLIC;"

# Find and execute all .sql files in the data directory
SQL_FILES=$(find "$DATA_DIR" -name "*.sql" -type f | sort)

if [ -z "$SQL_FILES" ]; then
    echo "Warning: No .sql files found in $DATA_DIR"
    exit 0
fi

for sql_file in $SQL_FILES; do
    echo "Executing: $(basename "$sql_file")"
    psql -f "$sql_file"
done

echo "Database reinitialization complete."

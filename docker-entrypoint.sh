#!/bin/sh
set -e

UVICORN_RELOAD_ARGS=""

echo "Migrating database"

if ! alembic -c src/infrastructure/db/alembic.ini upgrade head; then
    echo "Database migration failed! Exiting container..."
    exit 1
fi

echo "Migrations deployed successfully"


if [ "$UVICORN_RELOAD_ENABLED" = "true" ]; then
    echo "Uvicorn will run with reload enabled"
    UVICORN_RELOAD_ARGS="--reload --reload-dir /opt/pravschool_bot/src --reload-dir /opt/pravschool_bot/assets --reload-include *.ftl"
else
    echo "Uvicorn will run without reload"
fi

exec uvicorn src.__main__:application --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-5000}" --factory --use-colors ${UVICORN_RELOAD_ARGS}
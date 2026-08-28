#!/bin/sh
set -e

# ==============================================================================
# AIRA Production Backend Entrypoint Script
# Handles optional pre-startup database migrations and graceful process exec.
# ==============================================================================

if [ "$RUN_MIGRATIONS" = "true" ] || [ "$RUN_MIGRATIONS" = "1" ]; then
    echo "[AIRA-ENTRYPOINT] RUN_MIGRATIONS is enabled. Running database migrations..."
    flask db upgrade
    echo "[AIRA-ENTRYPOINT] Database migrations completed successfully."
fi

echo "[AIRA-ENTRYPOINT] Starting application process: $@"
exec "$@"

#!/bin/sh
# Entrypoint script that handles PORT environment variable

# Default to port 8000 if PORT is not set
PORT=${PORT:-8000}

echo "Starting application on port ${PORT}"

# Run Gunicorn with the correct port
exec gunicorn backend.main:app \
    -k uvicorn.workers.UvicornWorker \
    --bind "0.0.0.0:${PORT}" \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info


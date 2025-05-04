#!/bin/bash
set -e

# Run the database initialization script first
echo "Initializing database..."
python -m app.core.db_init

# Start the application with gunicorn and uvicorn workers
echo "Starting the application..."
exec python -m debugpy \
    --listen 0.0.0.0:7000 \
    -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
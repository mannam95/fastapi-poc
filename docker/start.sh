#!/bin/bash
set -e

# Run the database initialization script first
echo "Initializing database..."
python -m app.core.db_init

# Start the application with gunicorn and uvicorn workers
echo "Starting the application..."
exec gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers "$WORKERS" \
    --bind 0.0.0.0:8000 
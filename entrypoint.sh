#!/bin/sh
set -e

echo "=== Ensuring data directory exists ==="
mkdir -p /app/data

echo "=== Initializing database ==="
python -c 'from app.main import app; from app.models import db; app.app_context().push(); db.create_all()' || {
    echo "ERROR: Database initialization failed"
    exit 1
}
echo "=== Database initialized ==="

echo "=== Starting gunicorn ==="
exec gunicorn --bind 0.0.0.0:3000 --workers 2 --timeout 60 app.main:app
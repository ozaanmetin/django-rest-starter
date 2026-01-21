#!/bin/bash
set -e

echo "Starting gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 4 \
    --access-logfile - \
    --error-logfile -

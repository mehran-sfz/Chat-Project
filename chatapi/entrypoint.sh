#!/bin/bash

# Generate SECRET_KEY dynamically
export SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --no-input --clear

# Start Gunicorn server
echo "Starting Uvicorn server..."
daphne -u /tmp/daphne.sock -b 0.0.0.0 -p 8000 chatapi.asgi:application
#!/usr/bin/env sh
set -e

# Apply migrations & collect static (idempotent)
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn webapp.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60

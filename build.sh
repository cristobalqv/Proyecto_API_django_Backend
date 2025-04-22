#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

python manage.py makemigrations

# Apply any outstanding database migrations
python manage.py migrate

# Validar si existe superuser, sino crearlo
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0) if User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists() else exit(1)" || \
python manage.py createsuperuser --noinput 
# python -m gunicorn myproject.asgi:application -k uvicorn.workers.UvicornWorker
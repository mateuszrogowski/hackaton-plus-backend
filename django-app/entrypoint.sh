#!/usr/bin/env bash

set -e

echo "${0}: running migrations."
python manage.py migrate --noinput
echo "${0}: collecting statics."
python manage.py collectstatic --noinput

echo "from django.contrib.auth.models import User; print('Admin exists') if User.objects.filter(username='mrogowski').exists() else User.objects.create_superuser('mrogowski', 'mateusz@rogowski.science', '123')" | python manage.py shell

# Prepare log files and start outputting logs to stdout
touch /logs/gunicorn.log
touch /logs/gunicorn-access.log
# tail -n 0 -f /logs/gunicorn*.log &

gunicorn hackaton_plus.wsgi:application \
   --name hackaton_plus \
   --bind 0.0.0.0:8000 \
   --timeout 600 \
   --workers 3 \
   --log-level=info \
   --log-file=/logs/gunicorn.log \
   --access-logfile=/logs/gunicorn-access.log

"$@"

#!/usr/bin/env bash

set -e

echo "Cleaning *.pyc files"
find . -name "*.pyc" -exec rm -f {} \;

echo "${0}: running migrations."
python manage.py migrate --noinput
echo "${0}: collecting statics."
python manage.py collectstatic --noinput

echo "from django.contrib.auth.models import User; print('Admin exists') if User.objects.filter(username='mrogowski').exists() else User.objects.create_superuser('mrogowski', 'mateusz@rogowski.science', '123')" | python manage.py shell

python manage.py runserver 0.0.0.0:8000

"$@"

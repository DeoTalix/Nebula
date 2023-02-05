#!/bin/bash
source .venv/bin/activate
cd mailservice
(trap 'kill 0' SIGINT; ngrok http 8000 &>/dev/null & celery -A mailservice worker -l info &>/dev/null & celery -A mailservice beat -l info &>/dev/null & python manage.py runserver 8000)

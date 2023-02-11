#!/bin/sh
echo
echo "Activating virtual environment"
echo "------------------------------"
. .venv/bin/activate
echo
echo "Launching 3 background processes"
echo "--------------------------------" 
echo "ngrok, celery worker, celery beat"
echo
echo "Launching django server"
echo "-----------------------"
echo "Note: stopping django server will also stop background processes"
echo
cd mailservice
(trap 'kill 0' SIGINT; \
ngrok http 8000 &>/dev/null & \
celery -A mailservice worker -l info &>/dev/null & \
celery -A mailservice beat -l info &>/dev/null & \
sleep 3 && \
gunicorn -b 0.0.0.0:8000 mailservice.wsgi:application)

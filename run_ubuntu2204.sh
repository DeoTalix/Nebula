#!/bin/bash
echo
echo "Activating virtual environment"
echo "------------------------------"
source .venv/bin/activate
echo
echo "Entering mailservice working directory"
echo "--------------------------------------"
cd mailservice
echo
echo "Launching 3 background processes"
echo "--------------------------------" 
echo "ngrok, celery worker, celery beat"
echo
echo "Launching django server"
echo "-----------------------"
echo "Note: stopping django server will also stop background processes"
echo
(trap 'kill 0' SIGINT; ngrok http 8000 &>/dev/null & celery -A mailservice worker -l info &>/dev/null & celery -A mailservice beat -l info &>/dev/null & python manage.py runserver 8000)

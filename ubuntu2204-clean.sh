#!/bin/sh
echo
echo "Removing: .venv, .env, db.sqlite3, staticfiles, logs, migrations"
rm -rf .venv
rm .env
rm -rf mailservice/db.sqlite3
rm -rf mailservice/staticfiles
rm -rf mailservice/app/migrations
rm -f mailservice/logs/*.log
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
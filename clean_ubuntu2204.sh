#!/bin/bash
echo
echo "Removing: .venv, .env, db.sqlite3, staticfiles, logs, migrations"
rm -rf .venv
rm .env
rm -rf mailservice/db.sqlite3
rm -rf mailservice/staticfiles
rm -rf mailservice/logs
rm -rf mailservice/app/migrations

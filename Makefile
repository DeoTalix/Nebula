.PHONY: install_rabbitmq config_rabbitmq install_python install_pip \
install_venv install_requirements setup_dotenv setup_django create_superuser \
install_ngrok config_ngrok setup run clean

VENV_PATH = .venv
PYTHON = /usr/bin/python2.7
PIP = /usr/bin/pip2
REQ_PATH = requirements.txt
VENV = /usr/bin/virtualenv
VENV_PYTHON = $(VENV_PATH)/bin/python
VENV_PIP = $(VENV_PATH)/bin/pip

clean:
	echo
	echo "Removing: .venv, .env, db.sqlite3, staticfiles, logs, migrations"
	rm -rf $(VENV_PATH)
	rm .env
	rm -rf mailservice/db.sqlite3
	rm -rf mailservice/staticfiles
	rm -rf mailservice/app/migrations
	rm -f mailservice/logs/*.log
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

install_rabbitmq:
	echo
	echo "Installing rabbitmq-server"
	echo "--------------------------"
	sudo apt install rabbitmq-server

config_rabbitmq:
	echo
	echo "Configuring rabbitmq-server"
	echo "--------------------------"
	sudo rabbitmqctl add_user myuser mypassword
	sudo rabbitmqctl add_vhost myvhost
	sudo rabbitmqctl set_user_tags myuser mytag
	sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"

install_python:
	echo
	echo "Installing python2"
	echo "------------------"
	sudo apt install python2

install_pip: $(PYTHON)
	echo
	echo "Installing pip"
	echo "--------------"
	sudo apt install python-pip
	$(PIP) install -U pip

install_venv: $(PIP)
	echo
	echo "Installing virtual environment"
	echo "------------------------------"
	$(PIP) install virtualenv

# activate_venv:
# 	echo
# 	echo "Activating virtual environment"
# 	echo "------------------------------"
# 	$(VENV) -p $(PYTHON) $(VENV_PATH)
# 	. $(VENV_PATH)/bin/activate

install_requirements: $(REQ_PATH)
	echo
	echo "Installing pip requirements"
	echo "---------------------------"
	$(VENV_PIP) install -r $(REQ_PATH)

setup_dotenv:
	echo
	echo "Setting up .env"
	echo "---------------"
	touch .env
	read -p "Email host: " email_host
	sudo echo "EMAIL_HOST='$email_host'" >> .env
	read -p "Email port: " email_port
	sudo echo "EMAIL_PORT=$email_port" >> .env
	read -p "Email host user (username@emailhost.com): " email_host_user
	sudo echo "EMAIL_HOST_USER='$email_host_user'" >> .env
	read -s -p "Email host password: " email_host_password
	sudo echo "EMAIL_HOST_PASSWORD='$email_host_password'" >> .env
	sudo echo "CELERY_USER=myuser" >> .env
	sudo echo "CELERY_PASSWORD=mypassword" >> .env
	sudo echo "CELERY_HOST=myvhost" >> .env

setup_django: mailservice/db.sqlite3 mailservice/app/fixtures/Person.json
	echo
	echo "Setting up django"
	echo "-----------------"
	cd mailservice && \
	$(VENV_PYTHON) manage.py migrate --run-syncdb && \
	$(VENV_PYTHON) manage.py loaddata app/fixtures/Person.json && \
	$(VENV_PYTHON) manage.py collectstatic

create_superuser: setup_django
	echo
	echo "Create new django superuser"
	echo "---------------------------"
	cd mailservice && \
	$(VENV_PYTHON) manage.py createsuperuser

install_ngrok:
	echo
	echo "Installing ngrok"
	echo "----------------"
	sudo snap install ngrok

config_ngrok:
	echo
	echo "You will need an authtoken to be able to use ngrok."
	echo "Visit https://dashboard.ngrok.com/get-started/setup and copy authtoken to the next promt."
	echo
	read -p "Paste ngork authtoken here: " ngrokauthtoken 
	ngrok config add-authtoken $ngrokauthtoken

setup: requrements.txt
	echo
	echo "All set"

run: setup
	echo
	echo "Activating virtual environment"
	echo "------------------------------"
	echo
	echo "Entering mailservice working directory"
	echo "--------------------------------------"
	echo
	echo "Launching 3 background processes"
	echo "--------------------------------" 
	echo "ngrok, celery worker, celery beat"
	echo
	echo "Launching django server"
	echo "-----------------------"
	echo "Note: stopping django server will also stop background processes"
	echo
	. .venv/bin/activate && \
	cd mailservice && \
	(\
		trap 'kill 0' SIGINT; \
		ngrok http 8000 &>/dev/null & \
		celery -A mailservice worker -l info &>/dev/null & \
		celery -A mailservice beat -l info &>/dev/null & \
		sleep 3 && \
		gunicorn -b 0.0.0.0:8000 mailservice.wsgi:application\
	)
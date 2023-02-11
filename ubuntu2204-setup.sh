#!/bin/sh
mkdir -p mailservice/logs
echo
echo "Installing rabbitmq-server"
echo "--------------------------"
sudo apt install rabbitmq-server
echo
echo "Setting up rabbitmq-server"
echo "--------------------------"
sudo rabbitmqctl add_user myuser mypassword
sudo rabbitmqctl add_vhost myvhost
sudo rabbitmqctl set_user_tags myuser mytag
sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"
echo
echo "Installing python2"
echo "------------------"
sudo apt install python2
echo
echo "Installing pip"
echo "--------------"
sudo apt install python-pip
pip install -U pip
echo
echo "Installing virtual environment"
echo "------------------------------"
python2 -m pip install virtualenv
echo
echo "Activating virtual environment"
echo "------------------------------"
python2 -m virtualenv -p /usr/bin/python2.7 .venv
. .venv/bin/activate
echo
echo "Installing pip requirements"
echo "---------------------------"
pip install -r requirements.txt
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
echo
echo
echo "Setting up django"
echo "-----------------"
cd mailservice
python manage.py migrate --run-syncdb
python manage.py loaddata app/fixtures/Person.json
python manage.py collectstatic
echo
echo "Create new django superuser"
echo "---------------------------"
python manage.py createsuperuser
echo
echo "Installing ngrok"
echo "----------------"
sudo snap install ngrok
echo
echo "You will need an authtoken to be able to use ngrok."
echo "Visit https://dashboard.ngrok.com/get-started/setup and copy authtoken to the next promt."
echo
read -p "Paste ngork authtoken here: " ngrokauthtoken 
ngrok config add-authtoken $ngrokauthtoken
echo
echo "All done"

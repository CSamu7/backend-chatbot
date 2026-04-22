#!/bin/sh
#Migraciones de la base de datos
python ./chatbot/manage.py migrate 

python ./chatbot/manage.py createsuperuser --email test@prueba.com --username samu --noinput

python ./chatbot/manage.py runserver 0.0.0.0:8000
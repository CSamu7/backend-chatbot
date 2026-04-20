#!/bin/sh
#Migraciones de la base de datos
python ./chatbot/manage.py migrate 
#Ejecutar server
python ./chatbot/manage.py runserver 
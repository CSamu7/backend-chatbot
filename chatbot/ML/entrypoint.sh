#!/bin/sh
set -e

echo "Ejecutando migraciones de Django..."
python chatbot/manage.py migrate --noinput

echo "Iniciando servidor Django..."
python chatbot/manage.py runserver 0.0.0.0:8000

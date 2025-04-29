#!/bin/bash
python manage.py migrate
gunicorn Procfile.wsgi:application --bind 0.0.0.0:$PORT

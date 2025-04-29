#!/bin/bash
python manage.py migrate
gunicorn Procfile.wsgi:Procfile --bind 0.0.0.0:$PORT

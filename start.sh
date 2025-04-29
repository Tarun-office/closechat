#!/bin/bash
python manage.py migrate
gunicorn yourprojectname.wsgi:Procfile --bind 0.0.0.0:$PORT
#!/bin/bash
python manage.py migrate
gunicorn gamification_config.wsgi --log-file -

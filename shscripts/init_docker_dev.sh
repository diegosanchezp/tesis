#!/bin/bash

source .venv/bin/activate && \
gunicorn --log-level DEBUG --reload \
  --reload-engine poll \
  --keyfile mkcert/key.pem \
  --certfile mkcert/cert.pem \
  --timeout 0 \
  --bind 0.0.0.0:8000 django_src.wsgi
# python manage.py runserver 0.0.0.0:8000

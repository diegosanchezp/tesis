#!/bin/bash

# Load environment variables
source ~/.zprofile

sudo --preserve-env docker compose stop && \

# Force update static files in the django_static_files volume
# otherwise it will use old stuff
sudo --preserve-env docker compose run --rm django python manage.py collectstatic \
  --settings django_src.settings.production \
  --noinput

# Update docker image for django service
sudo --preserve-env docker pull --quiet "$DOCKER_IMAGE" &> /dev/null && \

# Start again everything
sudo --preserve-env docker compose up -d

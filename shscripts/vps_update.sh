#!/bin/bash

# Load environment variables
source ~/.zprofile

cd ~/tesis

# Make a backup
sudo --preserve-env docker compose run --rm \
  --user "$(id -u)" \
  --env "ENVIRONMENT=production" \
  --volume "$HOME/fixture_backups:/app/fixture_backups" \
  --volume "./shscripts/:/app/shscripts/" \
  django python -m shscripts.backup && \

# Update the git repository
git pull

# Stop all docker services
sudo --preserve-env docker compose stop && \

# Update docker image for django service, supress all output
sudo --preserve-env docker pull --quiet "$DOCKER_IMAGE" &> /dev/null && \

# Force update static files in the django_static_files volume
# otherwise it will use old stuff
sudo --preserve-env docker compose run --rm django python manage.py collectstatic \
  --settings django_src.settings.production \
  --noinput && \

sudo --preserve-env docker compose start postgres && \

# Update the database models
sudo --preserve-env docker compose run --rm django \
    python manage.py migrate --settings django_src.settings.production && \

# Start again everything
sudo --preserve-env docker compose up -d

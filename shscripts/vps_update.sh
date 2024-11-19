#!/bin/bash

# Load environment variables
source ~/.zprofile

cd ~/repos/tesis

# Make a backup, $REPODIR flag is defined in ~/.zprofile
docker compose run --rm \
  --user "$(id -u)" \
  --env "ENVIRONMENT=production" \
  --volume "$HOME/fixture_backups:/app/fixture_backups" \
  --volume "$REPODIR/shscripts:/app/shscripts" \
  django python -m shscripts.backup && \

# Update the git repository
git pull

# Stop all docker services
docker compose stop && \

# Update docker image for django service, supress all output
docker pull --quiet "$DOCKER_IMAGE" &> /dev/null && \

# Force update static files in the django_static_files volume
# otherwise it will use old stuff
docker compose run --rm django python manage.py collectstatic \
  --settings django_src.settings.production \
  --noinput && \

docker compose start postgres && \

# Update the database models
docker compose run --rm django \
    python manage.py migrate --settings django_src.settings.production && \

# Start again everything
docker compose up -d

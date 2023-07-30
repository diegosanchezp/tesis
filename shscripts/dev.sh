#!/bin/bash

# Load common variables

SCRIPT_FILE_PATH=$(realpath "${BASH_SOURCE[0]:-$0}")
SCRIPT_DIR=$(dirname "$SCRIPT_FILE_PATH")
# ../../
ROOT_DIR=$(dirname "$SCRIPT_DIR")
COMPOSE_FILE=$ROOT_DIR/docker/dev/docker-compose.yml
WORKDIR="/app" # Docker container working directory

export COMPOSE_FILE

export DOCKER_BUILDKIT=1

cterm(){
  docker-compose run --rm --no-deps -w /app --entrypoint "bash" django
}


# Wrapper command
dockerpy(){
  docker-compose run --rm --no-deps -w /app --entrypoint "bash -c 'source .venv/bin/activate && $*'" django
}

managepy(){
  dockerpy python manage.py "$@"
}

helpmanage(){
  dockerpy python manage.py "$1" --help
}

create-app(){
  APP_NAME="$1"
  DJANGO_DIR="$WORKDIR/django_src"
  APP_DIR="$DJANGO_DIR/apps/$APP_NAME"

  # The following commands execute in the docker context
  dockerpy mkdir "$APP_DIR" && \
  ( managepy startapp "$APP_NAME" "$APP_DIR" || \
  # remove the created directory
    dockerpy rm -r "$APP_DIR" )
}

resetdb(){
  docker-compose stop django && \
  dockerpy python shscripts/reset_db.py && \
  docker-compose start django
}

# Docker related
alias runserver='docker-compose run --rm --service-ports django'
alias logs='docker-compose logs --no-log-prefix -f django'

# Python related
alias pyterm="dockerpy bash"
alias djshell="managepy shell"

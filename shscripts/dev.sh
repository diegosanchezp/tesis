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
export AWS_PROFILE="tesis-infra"

cterm(){
  docker-compose run --rm --no-deps -w /app --entrypoint "bash" django
}

load_env(){
  set -a
  source ${1:-.env}
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
    docker-compose start postgres && \
    docker-compose stop django && \
    # Use -m flag to add shscript to sys.path
    # otherwise import error will arise
    dockerpy python -m shscripts.reset_db "$@"
}

backupdb(){
  dockerpy ENVIRONMENT=development python -m shscripts.backup
}
# Docker related
runserver(){
  docker-compose run --rm --service-ports django
}
alias logs='docker-compose logs --no-log-prefix -f django'

# Python related
alias pyterm="dockerpy zsh"
alias djshell="managepy shell"

pygrep(){
  grep --exclude-dir=.git --exclude-dir=node_modules \
    --exclude-dir=.venv --exclude-dir=.lvenv \
    --exclude-dir=.pipcache --exclude-dir=mkcert "$@"
}

blackfmt(){
  dockerpy black --target-version py311 "$@"
}

fmtfiles(){
  # Format python files that are going to be commited
  dockerpy 'git diff --name-only --cached | grep "\.py$" | xargs black --target-version py311 --verbose'
}

fmtlastfiles(){
  dockerpy 'git log -1 --name-only --pretty=format: | grep "\.py$" | xargs black --target-version py311 --verbose'
}

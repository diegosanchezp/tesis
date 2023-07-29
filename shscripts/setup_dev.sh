#!/bin/bash

SCRIPT_FILE_PATH=$(realpath "${BASH_SOURCE[0]:-$0}")
SCRIPT_DIR=$(dirname "$SCRIPT_FILE_PATH")
# ../../
ROOT_DIR=$(dirname "$SCRIPT_DIR")
COMPOSE_FILE=$ROOT_DIR/docker/dev/docker-compose.yml

export COMPOSE_FILE

echo "SETUP DJANGO IN DOCKER"
docker-compose up -d postgres && \
docker-compose run -w /app --entrypoint bash --rm django shscripts/setup_docker_dev.sh && \

docker-compose run -u root -w /app --entrypoint bash --rm django shscripts/generate-certificates.sh && \

echo "Creating private env file"
cp "$ROOT_DIR"/envs/private.env.template "$ROOT_DIR"/envs/.private.env

echo "=== LOAD COMMAND UTILITIES with command ===" && \

echo "source \"$SCRIPT_DIR/dev.sh\""



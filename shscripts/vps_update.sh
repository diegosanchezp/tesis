#!/bin/bash

# Load environment variables
source ~/.zprofile

# Update docker image for django service
sudo --preserve-env docker compose stop && \
sudo --preserve-env docker pull --quiet "$DOCKER_IMAGE" &> /dev/null && \
sudo --preserve-env docker compose up -d

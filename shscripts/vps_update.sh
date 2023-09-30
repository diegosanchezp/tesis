#!/bin/bash

# Load environment variables
source ~/.zprofile

# Go to the root folder of the repo
cd ..
docker compose stop
docker pull "$DOCKER_IMAGE"
docker compose up -d

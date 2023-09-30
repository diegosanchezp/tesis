#!/bin/bash

# Load environment variables
source ~/.zprofile

# Go to the root folder of the repo
cd ..
sudo --preserve-env docker compose stop
sudo --preserve-env docker pull "$DOCKER_IMAGE"
sudo --preserve-env docker compose up -d

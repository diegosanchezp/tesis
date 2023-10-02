#!/bin/bash

# These commands were used to setup an ec2 debian instance
# it is not intended to be executed
# DO NOT RUN the whole script
sudo apt-get update

# tesis sys dependencies
# git

# docker
# ca-certificates curl

sudo apt-get install ca-certificates curl gnupg git neovim zsh zsh-syntax-highlighting stow

# Add Docker's official GPG key:
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Reboot has to be performed from this point here, see
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-reboot.html

# Clone repo
git clone https://github.com/diegosanchezp/tesis.git

# install stow
cd tesis/vpsconf
stow --no-folding --verbose --target ~ zsh/
# zsh setup
mkdir ~/.cache/zsh/
touch ~/.cache/zsh/history

# change default shell to zsh
sudo usermod -s /bin/zsh $USER
# return back
cd ..

# Prepare environment variables files

ROOT_DIR=".."

cp "$ROOT_DIR"/envs/production/host.template "$ROOT_DIR"/envs/production/host
cp "$ROOT_DIR"/envs/production/django.template "$ROOT_DIR"/envs/production/django
cp "$ROOT_DIR"/envs/production/postgres.template "$ROOT_DIR"/envs/production/postgres

# Now add the environment variables manually
# random secret key can be generated with

# from django.core.management.utils import get_random_secret_key
# get_random_secret_key()
load_env env/production/host

# Generate http certs

sudo --preserve-env docker pull "$DOCKER_IMAGE"

sudo --preserve-env docker run --rm \
--env-file envs/production/django \
--mount 'type=bind,source=./nginx,destination=/app/nginx' \
--mount 'type=bind,source=./shscripts,destination=/app/shscripts,readonly' \
--interactive --tty \
"$DOCKER_IMAGE" \
python shscripts/generate_templates.py

sudo --preserve-env docker compose up -d postgres

sudo --preserve-env docker compose run --rm django \
    python manage.py migrate --settings django_src.settings.production

sudo --preserve-env docker compose up -d

# After installing the sshd config restart the daemon
sudo systemctl restart sshd.service


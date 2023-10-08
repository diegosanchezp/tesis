#!/bin/bash
sudo --preserve-env docker compose start postgres

sudo --preserve-env docker compose run --rm \
  --env "ENVIRONMENT=production" \
  --user "$(id -u)" \
  --volume "$HOME/fixture_backups:/app/fixture_backups" \
  django python -m shscripts.backup

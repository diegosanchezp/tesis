#!/bin/bash
sudo --preserve-env docker compose start postgres

sudo --preserve-env docker run --rm \
  --name backup_prod \
  --workdir /app \
  --mount "type=bind,source=$HOME/fixture_backups,target=/app/fixture_backups" \
  --user "$(id -u)" \
  --env "ENVIRONMENT=production" \
  --env-file envs/production/django \
  --env-file envs/production/postgres \
  --network production_default \
  "$DOCKER_IMAGE" \
  python -m shscripts.backup

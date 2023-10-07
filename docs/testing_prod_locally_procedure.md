# Local production testing procedure
How to test the production Docker images locally

First, set the environment for the services in these locations, similar structure for `envs/dev`

- `envs/production/django`
- `envs/production/postgres`

Note: you might want to put the private environment variables of `envs/private.env.template` in `envs/production/django`

Set the required environment variables for the docker host

```bash
export COMPOSE_FILE=docker/production/docker-compose.yml
export DOCKER_IMAGE=ghcr.io/diegosanchezp/django_egresados:latest

# Also these can be stored on a file: envs/production/host
load_env envs/production/host
```

Build the production image for Django

``` bash
docker build -f docker/production/Dockerfile --tag "$DOCKER_IMAGE" .
```

Render all config files that use jinja2

```bash
docker run --rm \
--env-file envs/production/django \
--mount 'type=bind,source=./nginx,destination=/app/nginx' \
--mount 'type=bind,source=./shscripts,destination=/app/shscripts,readonly' \
--interactive --tty \
"$DOCKER_IMAGE" \
python shscripts/generate_templates.py
```

Start all services in detached mode

```bash
docker-compose up --detach
```

Run migrations ( create database tables )

```bash
docker compose run --rm django \
    python manage.py migrate --settings django_src.settings.production
```

Upload testing fixtures to database

```bash
docker compose run --rm django python manage.py loaddata fixtures/wagtail_pages.json
```

## Testing backup procedure
```bash
mkdir ~/fixture_backups
```

```bash
docker run --rm \
  --name backup_prod \
  --workdir /app \
  --mount "type=bind,source=$HOME/fixture_backups,target=/app/fixture_backups" \
  --mount "type=bind,source=./shscripts/,target=/app/shscripts/" \
  --user "$(id -u)" \
  --env "ENVIRONMENT=production" \
  --env-file envs/production/django \
  --env-file envs/production/postgres \
  --network production_default \
  "$DOCKER_IMAGE" \
  python -m shscripts.backup
```

## Debugging the service containers


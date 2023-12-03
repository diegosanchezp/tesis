# Local production testing procedure
How to test the production Docker images locally

First, set the environment for the services in these locations, similar structure for `envs/dev`

- `envs/production/django`
- `envs/production/postgres`

Note: you might want to put the private environment variables of `envs/private.env.template` in `envs/production/django`

Set the required environment variables for the docker host

```bash
export COMPOSE_FILE=docker/production/docker-compose.yml:docker/production/docker.localprod.yml
export DOCKER_IMAGE=ghcr.io/diegosanchezp/django_egresados:latest
export DOCKER_BUILDKIT=1

# Also these can be stored on a file: envs/production/host
load_env envs/production/host
```

Install build kit, on archlinux:

```bash
sudo pacman -S docker-buildx
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

Update the staticfiles on django_static_files volume

```bash
docker compose run --rm django python manage.py collectstatic \
  --settings django_src.settings.production \
  --noinput
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
docker compose run --rm django python manage.py loaddata fixtures/admin.json fixtures/wagtail_pages.json
```

## Testing backup procedure
```bash
mkdir ~/fixture_backups
```

```bash
docker compose run --rm \
  --env "ENVIRONMENT=production" \
  --user "$(id -u)" \
  --volume "$HOME/fixture_backups:/app/fixture_backups" \
  --volume "./shscripts/:/app/shscripts/" \
  django python -m shscripts.backup
```
## Resetting the database
```bash
docker compose run --rm \
  --volume "$HOME/fixture_backups:/app/fixture_backups" \
  django python -m shscripts.reset_db
```

## Debugging the service containers


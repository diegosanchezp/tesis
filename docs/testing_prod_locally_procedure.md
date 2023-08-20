# Local production testing procedure
How to test the production Docker images locally

Set the environment for the services in these locations

- `envs/production/django`
- `envs/production/postgres`

Note: you might want to put the private environment variables of `envs/private.env.template` in `envs/production/django`

Set the `COMPOSE_FILE` environment variable

```bash
export COMPOSE_FILE=docker/production/docker-compose.yml
```

Build the production image for Django

``` bash
docker build -f docker/production/Dockerfile --tag django_prod_image:latest .
```

Start all services in detached mode

```bash
docker-compose up --detach
```

Copy the media files

```bash
docker compose cp media django:/app/media
```

Run migrations ( create database tables )

```bash
docker compose run --rm django python manage.py migrate
```

Upload testing fixtures to database

```bash
docker compose run --rm django python manage.py loaddata fixtures/wagtail_pages.json
```

## Debugging the service containers

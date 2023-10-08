# syntax=docker/dockerfile:1

# https://docs.docker.com/develop/develop-images/multistage-build/


# --- JS BUILD --- #
FROM node:18.17.1-slim as jsbuild
WORKDIR /app
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
COPY . ./

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
  corepack enable && pnpm install --frozen-lockfile

# Build javascript src files
RUN ls -al && pnpm run build

# --- PYTHON BUILD --- #
FROM python:3.11.4 AS djangoapp
WORKDIR /app
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# see .dockerignore to see which files are ignored
COPY . ./
COPY --from=jsbuild /app/static/dist ./static/dist
# Jsbuild

# Don’t delete the downloaded apt packages
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install apt packages, keep a cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y gettext \
  libnss3-tools

# Install python dependencies, keep a cache
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements/prod.txt

# Copy static files
RUN python manage.py collectstatic \
  --settings django_src.settings.production \
  --noinput

# Run the image as a non-root user
#RUN adduser -D myuser
#USER myuser

# syntax=docker/dockerfile:1

# https://docs.docker.com/develop/develop-images/multistage-build/

# --- PYTHON BUILD --- #
FROM python:3.10.6 AS djangoapp
# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
COPY . ./

# Don’t delete the downloaded apt packages
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install apt packages, keep a cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y gettext

# Install python dependencies, keep a cache
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements/prod.txt

# Copy static files
RUN python manage.py collectstatic --noinput
# Run the image as a non-root user
#RUN adduser -D myuser
#USER myuser

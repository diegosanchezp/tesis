# syntax=docker/dockerfile:1

# https://docs.docker.com/develop/develop-images/multistage-build/

# --- PYTHON BUILD --- #
FROM python:3.11.4 AS djangoapp

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . ./

# Don’t delete the downloaded apt packages
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Install apt packages, keep a cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt update && apt-get --no-install-recommends install -y gettext \
  libnss3-tools nodejs npm

# Install python dependencies, keep a cache
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements/prod.txt

# Install pnpm the package manager
RUN npm install -g pnpm

# https://pnpm.io/npmrc
# Install nodejs dependencies, keep a cache
RUN --mount=type=cache,target=/root/.cache/pnpm/ \
  --mount=type=cache,target=/root/.local/share/pnpm/store/ \
  pnpm install

# Build javascript src files & # Copy static files
RUN pnpm run build && \
  python manage.py collectstatic \
  --settings django_src.settings.production \
  --noinput

# Run the image as a non-root user
#RUN adduser -D myuser
#USER myuser

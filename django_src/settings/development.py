"""
Django settings for distribuidor_dj project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os

from .base import *  # noqa

# read environment files
ENV_DIR = BASE_DIR / "envs" / "dev"  # noqa F405
env.read_env(str(ENV_DIR / "django"))  # noqa F405
env.read_env(str(ENV_DIR / "postgres"))  # noqa F405

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

SECRET_KEY = env('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# https://docs.djangoproject.com/en/stable/ref/settings/#databases
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1", "host.docker.internal"]

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(BASE_DIR / "static"),
    # Include DJANGO_VITE_ASSETS_PATH into STATICFILES_DIRS to be copied inside
    # when run command python manage.py collectstatic
    DJANGO_VITE_ASSETS_PATH
]  # noqa F405

# If use HMR or not.
DJANGO_VITE_DEV_MODE = DEBUG
DJANGO_VITE_DEV_SERVER_PROTOCOL = "https"
# Media Files
# https://overiq.com/django-1-10/handling-media-files-in-django/
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa F405
MEDIA_URL = "/media/"


# https://github.com/benoitc/gunicorn/issues/1562#issuecomment-1530850143
# Gunicorn worker will have cached templates, so disable them in development
default_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "templates")],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "loaders": default_loaders,
        },
    },
]
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["console"],
#             "level": "DEBUG",
#         },
#     },
# }

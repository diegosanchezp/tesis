"""
Django settings for distribuidor_dj project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/stable/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/stable/ref/settings/
"""

from .base import *  # noqa

def load_env_array(envar_name: str):
    """
    Strip whitespaces for enviroment variables
    that are comma separated strings
    """

    return list(map(
        lambda x: x.strip(' '),
        env(envar_name).split(",")
    ))

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


# Javascript bundler config
# If use HMR or not.
DJANGO_VITE_DEV_MODE = DEBUG
DJANGO_VITE_DEV_SERVER_PROTOCOL = "https"

PRIVATE_MEDIA_ROOT = os.path.join(BASE_DIR, "private_media")

# https://github.com/benoitc/gunicorn/issues/1562#issuecomment-1530850143
# Gunicorn worker will have cached templates, so disable them in development
TEMPLATES[0]["OPTIONS"]["loaders"] = default_loaders

# WAGTAILADMIN_BASE_URL required for notification emails
WAGTAILADMIN_BASE_URL = f"https://{env('HOST_NAME')}:8000"

# Serve static and media files staticfiles
MIDDLEWARE.insert(3,"whitenoise.middleware.WhiteNoiseMiddleware")

ALLOWED_HOSTS = load_env_array("ALLOWED_HOSTS")

# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = load_env_array("CORS_ALLOWED_ORIGINS")

# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = load_env_array("CSRF_TRUSTED_ORIGINS")

# Should probably move this to a testing.py settings file
MEDIA_ROOT_TEST = os.path.join(BASE_DIR, "tests", "media")

# Wagtail needs this for send emails, otherwise might get
# OSError: [Errno 99] Cannot assign requested address, sending emails
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

import os

from .base import *  # noqa

def load_env_array(envar_name: str):
    """
    Strip whitespaces for enviroment variables
    that are comma separated strings
    """
    return list(map(
        lambda x: x.strip(' '),
        os.getenv(envar_name, "").split(",")
    ))

SECRET_KEY = env("SECRET_KEY")

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
        "ATOMIC_REQUESTS": True,
    }
}


ALLOWED_HOSTS = load_env_array("ALLOWED_HOSTS")

# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = load_env_array("CORS_ALLOWED_ORIGINS")

# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = load_env_array("CSRF_TRUSTED_ORIGINS")

# For NGINX
# https://stackoverflow.com/a/71482883
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-SECURE_SSL_REDIRECT
SECURE_SSL_REDIRECT = True

# # Wagtail preview uses iframes
# X_FRAME_OPTIONS = "SAMEORIGIN"

# TODO: test
WAGTAILADMIN_BASE_URL = "https://127.0.0.1"

TEMPLATES[0]["OPTIONS"]["loaders"] = cached_loaders

# Sends messages from the django logger of level INFO or higher to the console
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    },
}

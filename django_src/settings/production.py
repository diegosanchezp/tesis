import os

from .base import *  # noqa

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

ALLOWED_HOSTS = [
    # Nginx proxy
    "127.0.0.1",
    # docker-compose host
    "django",
]

# Media Files
# https://overiq.com/django-1-10/handling-media-files-in-django/
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa F405
MEDIA_URL = "/media/"

# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://django:8000",
]

CORS_ALLOW_ALL_ORIGINS = False

# --- HTTPS ---
# Mark CSRF_COOKIE  as “secure”, browsers may ensure that the cookie is only sent with an HTTPS connection
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# TODO: test
WAGTAILADMIN_BASE_URL = "https://127.0.0.1:8000"

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

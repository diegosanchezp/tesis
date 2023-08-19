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
    "localhost",
]


# https://pypi.org/project/django-cors-headers/
CORS_ALLOWED_ORIGINS = [
    # "http://127.0.0.1:8000",
    # "http://django:8000",
    "https://127.0.0.1:443",
    "https://127.0.0.1",
    # TODO: put here actual prod domain, maybe via env variable
]

# CORS_ALLOW_ALL_ORIGINS = False

CSRF_TRUSTED_ORIGINS = ['https://127.0.0.1', 'https://localhost']


# https://docs.djangoproject.com/en/stable/ref/settings/#secure-content-type-nosniff
# SECURE_CONTENT_TYPE_NOSNIFF = True

# For NGINX
# https://stackoverflow.com/a/71482883
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Wagtail preview
X_FRAME_OPTIONS = "SAMEORIGIN"

# --- HTTPS ---
# Mark CSRF_COOKIE  as “secure”, browsers may ensure that the cookie is only sent with an HTTPS connection
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

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

# STORAGES = {
#     "default": {
#         "BACKEND": "django.core.files.storage.FileSystemStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }

# Serve static and media files staticfiles
# MIDDLEWARE.insert(3,"whitenoise.middleware.WhiteNoiseMiddleware")

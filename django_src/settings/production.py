import os

from .base import *  # noqa


def load_env_array(envar_name: str):
    """
    Strip whitespaces for enviroment variables
    that are comma separated strings
    """
    return list(map(lambda x: x.strip(" "), os.getenv(envar_name, "").split(",")))


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
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# https://docs.djangoproject.com/en/stable/ref/settings/#std-setting-SECURE_SSL_REDIRECT
SECURE_SSL_REDIRECT = True

# # Wagtail preview uses iframes
# X_FRAME_OPTIONS = "SAMEORIGIN"
EMAIL_HOST=os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER=os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD=os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = 587
EMAIL_USE_TLS = True

BASE_URL = f"https://{os.getenv('HOST_NAME')}"
WAGTAILADMIN_BASE_URL = f"https://{os.getenv('HOST_NAME')}"
WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = os.getenv("WAGTAILADMIN_NOTIFICATION_FROM_EMAIL")
# The support email for requests / questions
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")

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

# wagtail storages

STORAGES = {
    # Media files are stored on s3
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    # Static files are stored in the docker image
    # and served with nginx
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# --- Django storages ---

# remove query parameter authentication from generated URLs, S3 buckets is public
# AWS_QUERYSTRING_AUTH=False
AWS_S3_SIGNATURE_VERSION = "s3v4"
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
# Do not allow overriding files on S3 as per Wagtail docs recommendation:
# https://docs.wagtail.io/en/stable/advanced_topics/deploying.html#cloud-storage
# Not having this setting may have consequences such as losing files.
AWS_S3_FILE_OVERWRITE = False

# Default ACL for new files should be "private" - not accessible to the
# public. Images should be made available to public via the bucket policy,
# where the documents should use wagtail-storages.
AWS_DEFAULT_ACL = "private"

# When signing URLs is enabled, the region must be set.
# The global S3 endpoint does not seem to support signed URLS.
# Set this only if you will be using signed URLs.
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")

# This settings lets you force using http or https protocol when generating
# the URLs to the files. Set https as default.
# https://github.com/jschneier/django-storages/blob/10d1929de5e0318dbd63d715db4bebc9a42257b5/storages/backends/s3boto3.py#L217
AWS_S3_URL_PROTOCOL = env("AWS_S3_URL_PROTOCOL")

# --- For local prod testing ---
# Custom S3 URL to use when connecting to S3, including scheme.
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")

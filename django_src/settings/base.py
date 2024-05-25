from pathlib import Path
import os
import environ
from django.utils.translation import gettext_lazy as _
from django.core.management.utils import get_random_secret_key

# Set env var defaults for the builds
env = environ.Env(
    SECRET_KEY=(str,get_random_secret_key()),
    GOOGLE_CLIENT_ID=(str, ""),
    GOOGLE_SECRET=(str,""),
    AWS_S3_REGION_NAME=(str,""),
    AWS_S3_URL_PROTOCOL=(str,"https:"),
    AWS_STORAGE_BUCKET_NAME=(str,"false_bucket_name"),
    ADMIN_USERNAME=(str,""),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Application definition
ADMIN_URL="admin/"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Needed for allauth
    "django.contrib.sites",
    # ---- Our apps ----
    "django_src.apps.api.apps.ApiConfig",
    "django_src.apps.main.apps.MainConfig",
    "django_src.apps.register.apps.RegisterConfig",
    "django_src.apps.auth.apps.AuthConfig",
    "django_src.pro_carreer.apps.ProCarreerConfig",
    "django_src.mentor.apps.MentorConfig",
    "django_src.student.apps.StudentConfig",
    # ---- Third party ----
    # API REST
    "rest_framework",
    "drf_spectacular",
    # JS
    'django_vite',
    # CSS
    # Forms
    "widget_tweaks",
    # HTMX
    "django_htmx",
    # CORS
    "corsheaders",
    # Alluth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # Alluth providers
    'allauth.socialaccount.providers.google',
    # Wagtail
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    # https://docs.wagtail.org/en/stable/advanced_topics/i18n.html#enabling-the-locale-management-ui-optional
    'wagtail.locales',
    'wagtail',
    'modelcluster',
    'taggit',
    # wagtail storages
    "wagtail_storages.apps.WagtailStoragesConfig",
    # UI component framework for Django
    "slippers",
]

# Required by allauth
SITE_ID = 1

MIDDLEWARE = [
    # CORS, hould be placed as high as possible
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Translation
    "django.middleware.locale.LocaleMiddleware",
    # wagtail
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    # django-htmx
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "django_src.urls"

default_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

cached_loaders = [("django.template.loaders.cached.Loader", default_loaders)]

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
            "builtins": ["slippers.templatetags.slippers"],
        },
    },
]

WSGI_APPLICATION = "django_src.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",  # noqa: E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",  # noqa: E501
    },
]

AUTH_USER_MODEL="customauth.User"

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
]

ADMIN_USERNAME=env("ADMIN_USERNAME")

# Enable internationalization in both Django and Wagtail
# https://docs.djangoproject.com/en/stable/topics/i18n/
TIME_ZONE = "UTC"
USE_I18N = True
WAGTAIL_I18N_ENABLED = True
USE_L10N = True
LANGUAGE_CODE = "es" # set default language as venezuelan spanish
USE_TZ = True
# Add supported languages (including English for potential fallback):
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]
# where message files will reside:
LOCALE_PATHS = [
    BASE_DIR / 'locale/',
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/
# Name of static files folder (after called python manage.py collectstatic)

# Where all static files from all aps are copied to
STATIC_ROOT = str(BASE_DIR / "staticfiles")  # noqa F405

# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"

STATIC_DIR_NAME = "static"

# Where ViteJS assets are built.
DJANGO_VITE_ASSETS_PATH = BASE_DIR / STATIC_DIR_NAME / "dist"

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(BASE_DIR / STATIC_DIR_NAME / "img"),
    # Include DJANGO_VITE_ASSETS_PATH into STATICFILES_DIRS to be copied inside
    # when run command python manage.py collectstatic
    DJANGO_VITE_ASSETS_PATH
]  # noqa F405

# Media Files
# https://overiq.com/django-1-10/handling-media-files-in-django/
# Where django saves user uploaded files
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa F405
# URL to fetch the saved user uploaded files
MEDIA_URL = "/media/"

REST_FRAMEWORK = {
    # YOUR SETTINGS
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Red Social Egresados API",
    "DESCRIPTION": "API de la Red Social egresados UCV",
    "VERSION": "1.0.0",
    # OTHER SETTINGS
}


SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # For each OAuth based provider, either add a ``SocialApp``
        # (``socialaccount`` app) containing the required client
        # credentials, or list them here:
        'APP': {
            'client_id': env('GOOGLE_CLIENT_ID'),
            'secret': env('GOOGLE_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        }
    }
}

WAGTAIL_SITE_NAME = 'Red Egresados UCV'

# --- Security settings --- #
CORS_ALLOW_ALL_ORIGINS = False

# --- HTTPS

# https://docs.djangoproject.com/en/stable/ref/settings/#secure-content-type-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True

# Mark CSRF_COOKIE  as “secure”, browsers may ensure that the cookie is only sent with an HTTPS connection
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

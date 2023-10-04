import os
import sys
import environ
from pathlib import Path

import django
from django.core.management import call_command

import psycopg2
from psycopg2 import errors
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

def read_env(BASE_DIR):
    """
    Read environment variables
    """

    env_dir = "production" if ENVIRONMENT == "production" else "dev"
    ENV_DIR = BASE_DIR / "envs" / env_dir
    env = environ.Env()
    env.read_env(str(ENV_DIR / "postgres"))
    env.read_env(str(ENV_DIR / "django"))
    return env

def create_connection(env: environ.Env):
    """
    Creates a psycopg2 connection object
    """

    # Establish a connection to database
    connection = psycopg2.connect(
        host=env("POSTGRES_HOST"),
        user=env("POSTGRES_USER"),
        password=env("POSTGRES_PASSWORD"),
        port=env("POSTGRES_PORT"),
        # Connect to template, otherwise db cant be dropped
        dbname="template1",
    )
    # https://pythontic.com/database/postgresql/create%20database
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    return connection

def drop_database(cursor):
    """
    """

    cursor.execute(f"DROP DATABASE IF EXISTS {env('POSTGRES_DB')}")

    # Create database and database user
    cursor.execute(f"CREATE DATABASE {env('POSTGRES_DB')};")
    try:
        cursor.execute(
            f"CREATE USER {env('POSTGRES_USER')} WITH PASSWORD '${env('POSTGRES_PASSWORD')}';"  # noqa: E501
        )
    except errors.DuplicateObject:
        # We don't want to stop the program
        pass

    cursor.execute(
        f"ALTER ROLE {env('POSTGRES_USER')} set client_encoding to 'utf8';"  # noqa: E501
    )
    cursor.execute(
        f"ALTER ROLE {env('POSTGRES_USER')} SET default_transaction_isolation TO 'read committed';"  # noqa: E501
    )
    cursor.execute(
        f"ALTER ROLE {env('POSTGRES_USER')} SET timezone TO 'America/Caracas';"  # noqa: E501
    )
    cursor.execute(
        f"GRANT ALL PRIVILEGES ON DATABASE {env('POSTGRES_DB')} TO {env('POSTGRES_USER')};"  # noqa: E501
    )
    cursor.execute(f"ALTER USER {env('POSTGRES_USER')} CREATEDB;")

def setup_django(BASE_DIR):
    """
    Load settings and populate Django’s application registry.
    This step is required django components in standalone mode.
    https://docs.djangoproject.com/en/4.2/topics/settings/#calling-django-setup-is-required-for-standalone-django-usage
    """

    # Tell python interpreter that it can look in the root repository for modules
    # otherwise we can't do imports like from django_src.settings
    sys.path.append(str(BASE_DIR))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_src.settings.development')
    django.setup()


def loaddata():
    """
    Load django fixtures
    """
    # name of fixtures, order matters
    FIXTURES = ["admin", "wagtail_pages"]

    FIXTURE_PATH = f"{os.environ.get('HOME')}/fixture_backups" if ENVIRONMENT == "production" else BASE_DIR / "fixtures"

    fixtures=[
        f"{FIXTURE_PATH}/{fname}.json" for fname in FIXTURES
    ]

    call_command("loaddata", *fixtures)

if __name__ == "__main__":

    setup_django(BASE_DIR)

    # Read environment files
    env = read_env(BASE_DIR)

    # Create a connection to the database
    connection = create_connection(env)

    cursor = connection.cursor()

    # Drop the database
    drop_database(cursor)

    # Close db connection
    connection.close()

    # === Rung Django manage.py commands ===

    # Apply migrations
    call_command("migrate")

    loaddata()

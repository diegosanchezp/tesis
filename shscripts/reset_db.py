import os
import environ

import subprocess as sp

import psycopg2
from psycopg2 import errors
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_src.settings.development')

def read_env(BASE_DIR):
    """
    Read environment variables
    """

    ENV_DIR = BASE_DIR / "envs" / "dev"
    env = environ.Env()
    env.read_env(str(ENV_DIR / "postgres"))
    env.read_env(str(ENV_DIR / "django"))
    return env


# Read environment files
env = read_env(BASE_DIR)


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
cursor = connection.cursor()

cursor.execute(f"DROP DATABASE IF EXISTS {env('POSTGRES_DB')}")

# Create database and database user
cursor.execute(f"CREATE DATABASE {env('POSTGRES_DB')};")
try:
    cursor.execute(
        f"CREATE USER {env('POSTGRES_USER')} WITH PASSWORD '${env('POSTGRES_PASSWORD')}';"  # noqa: E501
    )
except errors.DuplicateObject:
    # We don't want to stop program
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

# Close db connection
connection.close()

# === Rung Django manage.py commands ===

MANAGE = str(BASE_DIR / "manage.py")


# Apply migrations
sp.run(["python", MANAGE, "migrate"])

# name of fixtures, order matters
FIXTURES = ["admin"]

# Load fixtures
sp.run(
    [
        "python",
        MANAGE,
        "loaddata",
    ] + [
        f"fixtures/{fname}.json" for fname in FIXTURES
    ]
)

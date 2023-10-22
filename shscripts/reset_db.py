import logging
from pathlib import Path
import argparse

from django import db
from django.core.management import call_command
from django_src.apps.register.upload_data import upload_data as register_upload_data
import psycopg2
from psycopg2 import errors
import environ

# This lines have to come before the below import otherwise it will
# throw import error

# BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file
# sys.path.append(str(BASE_DIR))

# execute this file like this to avoid the lines above
# python -m shscripts.reset_db
from shscripts.backup import backup, setup, get_fixture_folder

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

    return connection


def drop_database(env: environ.Env):
    """
    Drop the whole database
    """

    # Create a connection to the database
    connection = create_connection(env)

    # A few commands (e.g. CREATE DATABASE, VACUUM, CALL on stored procedures using transaction control…) require to be run outside any transaction: in order to be able to run these commands from Psycopg, the connection must be in autocommit mode
    connection.autocommit = True

    cursor = connection.cursor()

    cursor.execute(f"DROP DATABASE IF EXISTS {env('POSTGRES_DB')}")

    # Create database and database user
    cursor.execute(f"CREATE DATABASE {env('POSTGRES_DB')};")

    # === Begin transaction ===
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

    # === End transaction ===
    connection.commit()

    # Close db connection
    cursor.close()
    connection.close()
    logging.info(msg="DATABASE successfully dropped")


def loaddata(BASE_DIR):
    """
    Restore a backup by Loading django fixtures
    """

    # Name of fixtures, this also defines the order in wich to load them
    FIXTURES = ["admin", "wagtail_pages"]

    FIXTURE_FOLDER = get_fixture_folder(BASE_DIR)

    fixtures=[
        f"{FIXTURE_FOLDER}/{fname}.json" for fname in FIXTURES
    ]

    call_command("loaddata", *fixtures)
    fixture_str = ", ".join(fixtures)
    logging.info(msg=f"fixtures {fixture_str} uploaded to the database")


def upload_data():
    """
    Put here all of the functions that use ORM models
    for uploading data
    """
    register_upload_data()

if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

    env = setup(BASE_DIR)

    # Beging parser setup
    parser = argparse.ArgumentParser(
        description="Reset database script"
    )

    parser.add_argument(
        "--dont_backup",
        help="Disable the database backup (use with caution)",
        action="store_true",
    )

    args = parser.parse_args()

    if not args.dont_backup:
        # backup the database
        backup(BASE_DIR)

    # Drop the database

    # Close all database connections oppened by django
    # so the database can be dropped
    db.connections.close_all()

    drop_database(env)

    # Apply migrations
    call_command("migrate", verbosity=1)
    logging.info("Database schema restored")

    # Load data to the database
    loaddata(BASE_DIR)
    upload_data()

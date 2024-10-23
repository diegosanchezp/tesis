from pathlib import Path
import logging
import argparse
from shscripts.backup import setup

import psycopg2
import environ
from psycopg2 import errors

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

"""
docker run --rm \
--network production_default \
--mount 'type=bind,source=./shscripts,destination=/app/shscripts' \
--env-file ./envs/production/postgres \
--env POSTGRES_DB=django_dev \
--interactive --tty \
"$DOCKER_IMAGE" \
python -m shscripts.drop_db
"""

# python -m shscripts.drop_db
if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

    env = setup(BASE_DIR)

    # Begin parser setup
    parser = argparse.ArgumentParser(
        description="Drop database script"
    )

    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop the database"
    )

    args = parser.parse_args()

    db_name = env('POSTGRES_DB')
    awnser = input(f"Drop database {db_name} ? y/n: ")
    if args.drop or awnser == "y":
        drop_database(env)

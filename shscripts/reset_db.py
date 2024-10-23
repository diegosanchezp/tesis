from enum import Enum
import logging
from pathlib import Path
import argparse


from django import db
from django.core.management import call_command
from django.conf import settings
from shscripts.drop_db import drop_database
from django_src.apps.main.dev_data import upload_dev_data
# This lines have to come before the below import otherwise it will
# throw import error

# BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file
# sys.path.append(str(BASE_DIR))

# execute this file like this to avoid the lines above
# python -m shscripts.reset_db
from shscripts.backup import backup, setup, get_fixture_folder



def loaddata(BASE_DIR):
    """
    Restore a backup by Loading django fixtures
    """

    # Name of fixtures, this also defines the order in wich to load them
    FIXTURES = ["admin", "wagtail_pages", "register"]

    FIXTURE_FOLDER = get_fixture_folder(BASE_DIR)

    fixtures=[
        f"{FIXTURE_FOLDER}/{fname}.json" for fname in FIXTURES
    ]

    call_command("loaddata", *fixtures)
    fixture_str = ", ".join(fixtures)
    logging.info(msg=f"fixtures {fixture_str} uploaded to the database")

class UploadAction(Enum):
    UPLOAD_DEV_DATA = "upload_dev_data"
    LOADDATA = "loaddata"

class SkipStep(Enum):
    MIGRATE = "migrate"
    DROP_DATABASE = "drop_database"
    UPLOAD_DATA = "upload_data"
    BACKUP = "backup"

steps_description = {
    "backup": {
        "description": "Make a backup of some of the tables",
    },
    "drop_database": {
        "description": "Delete the database",
    },
    "migrate": {
        "description": "Apply migrations, a.k.a create database tables",
    },
    "upload_data": {
        "description": "Insert data into the tables",
    },
}

def upload_data(BASE_DIR, action: UploadAction):
    """
    Put here all of the functions that use ORM models
    for uploading data
    """

    # For development mode use the testing fixtures
    if settings.DEBUG or action == UploadAction.UPLOAD_DEV_DATA.value:
        upload_dev_data()
    elif not settings.DEBUG or action == UploadAction.LOADDATA.value:
        # For now, only Load data fixtures to the database if we are resseting the production database
        loaddata(BASE_DIR)
    else:
        logging.info("Not uploading anything to the database")

def main():

    BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

    env = setup(BASE_DIR)

    # Beging parser setup
    parser = argparse.ArgumentParser(
        description="Reset database script"
    )

    parser.add_argument(
        "--upload-action",
        choices=[action.value for action in UploadAction],
        help="When the database is reseted, perform one the listed action"
    )

    # Add skipping options
    SKIP_PREFIX = "skip"
    for step_name, step_data in steps_description.items():
        parser.add_argument(
            f"--{SKIP_PREFIX}-{step_name}",
            help=f"Skip {step_data['description']}",
            action="store_true",
        )


    args = parser.parse_args()

    # backup the database first before dropping it
    if not getattr(args,f"{SKIP_PREFIX}_backup"):
        backup(BASE_DIR)


    # Drop the database
    if not getattr(args,f"{SKIP_PREFIX}_drop_database"):
        # Close all database connections oppened by django
        # so the database can be dropped
        db.connections.close_all()
        drop_database(env)


    # Apply migrations
    if not getattr(args,f"{SKIP_PREFIX}_migrate"):
        call_command("migrate", verbosity=1)
        logging.info("Database schema restored")


    # Insert data into tables
    if not getattr(args,f"{SKIP_PREFIX}_upload_data"):
        upload_data(BASE_DIR, args.upload_action)

if __name__ == "__main__":
    main()

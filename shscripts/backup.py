from dataclasses import dataclass
import sys
import json
import logging
from datetime import datetime
import os
from pathlib import Path

import django
from django.core.management import call_command

import environ


def get_environment():
    return os.environ.get("ENVIRONMENT", "development")

def read_env(BASE_DIR):
    """
    Read environment variables
    """

    ENVIRONMENT = get_environment()

    env_dir = "production" if ENVIRONMENT == "production" else "dev"
    ENV_DIR = BASE_DIR / "envs" / env_dir
    env = environ.Env()
    env.read_env(str(ENV_DIR / "postgres"))
    env.read_env(str(ENV_DIR / "django"))
    return env
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

def get_fixture_path(BASE_DIR):
    """
    Get the path of the fixture folder for different environments
    """
    ENVIRONMENT = get_environment()

    if ENVIRONMENT == "production":
        folder_path = BASE_DIR / "fixture_backups"

        # if the folder doesn't exists, create it
        if not folder_path.exists():
            folder_path.mkdir()
        return folder_path


    # default
    return BASE_DIR / "fixtures"

def get_fixture_meta(BASE_DIR) -> dict:
    """
    Reads the metafile and returns the meta dict
    that has the latest and previous folder names for backups
    """

    FIXTURE_PATH = get_fixture_path(BASE_DIR)

    metafile_path = FIXTURE_PATH / "fixture_meta.json"

    with open(metafile_path, 'r') as f:
        fixture_meta = json.load(f)

    return fixture_meta

def get_fixture_folder(BASE_DIR):

    ENVIRONMENT = get_environment()
    FIXTURE_PATH = get_fixture_path(BASE_DIR)
    FIXTURE_FOLDER = FIXTURE_PATH
    if ENVIRONMENT == "production":
        # Get the latest backup folder by reading the metafile
        fixture_meta = get_fixture_meta(BASE_DIR)
        FIXTURE_FOLDER: Path = FIXTURE_FOLDER / fixture_meta["latest"]
    return FIXTURE_FOLDER

@dataclass
class ModelBackup:
    models: list[str]
    output: str

def dumpdata(
    BASE_DIR: Path,
    extra_backups: list[ModelBackup] = [],
    backup_folder: Path | None = None
):
    """
    Makes the actual backups by calling manage.py loaddata
    - extra_backups: additional models to back up
    """

    if backup_folder is None:
        backup_folder = get_fixture_folder(BASE_DIR)

    # Put in this list backups that apply to all environments
    backups = [
        ModelBackup(
            models=["wagtailcore.Page", "wagtailcore.Site", "wagtailimages.Image", "main.HeroSection", "main.HomePage"],
            output=f"{backup_folder}/wagtail_pages.json",
        ),
    ] + extra_backups

    # Write backups to the folder
    for backup in backups:

        call_command(
            "dumpdata",
            *backup.models,
            natural_foreign=True,
            natural_primary=True, indent=4,
            output=backup.output,
            traceback=True,
            verbosity=2,
        )

        logging.info(msg=f"Backup saved to {backup.output}")

def backup_dev(BASE_DIR):
    backup_folder = get_fixture_folder(BASE_DIR)
    # Rare are the cases when I want to update the version controlled
    # fixtures just in case, save it to another dir.

    # later they can be copied or moved back to the fixtures dir, ex:
    # mv fixtures/tmp/wagtail.json fixtures/wagtail
    tmp_backup = backup_folder / "tmp"
    if not tmp_backup.exists():
        tmp_backup.mkdir()

    dumpdata(BASE_DIR, backup_folder=tmp_backup)

def backup_prod(BASE_DIR):
    """
    Create fixtures of specific models
    """

    FIXTURE_PATH = get_fixture_path(BASE_DIR)

    prefix = "latest_"

    # convert todays date to string with a specific format
    today = datetime.today().strftime("%Y_%m_%d_%H.%M.%S")

    # craft the folder name
    folder_name = f"{prefix}{today}"

    # Make sure that this is a folder
    assert FIXTURE_PATH.is_dir()

    backup_folder = FIXTURE_PATH / folder_name

    # Make the latest backup folder
    backup_folder.mkdir()

    metafile_path = FIXTURE_PATH / "fixture_meta.json"

    try:
        # Update the fixture metafile
        fixture_meta = get_fixture_meta(BASE_DIR)
        # Set the old latest as previous
        fixture_meta["previous"] = fixture_meta["latest"].removeprefix(prefix)

        # Rename old latest folder
        prev_backup_folder: Path = FIXTURE_PATH / fixture_meta["latest"]
        prev_backup_folder.rename(FIXTURE_PATH / fixture_meta["previous"])

        # Set the new folder as the latest
        fixture_meta["latest"] = folder_name

    except OSError:
        # Create the fixture metafile, since the file doesn't exists
        fixture_meta = {
            "previous": "",
            "latest": folder_name,
        }

    # update the meta json file
    with open(metafile_path, 'w') as f:
        f.write(json.dumps(fixture_meta, indent=4))

    # Call all dumpdata commands, it requires the fixture metafile
    # so is has to be called after is created
    dumpdata(
        BASE_DIR,
        extra_backups = [
            ModelBackup(
                models=["auth.User"],
                output=f"{backup_folder}/admin.json",
            )
        ]
    )

def backup(BASE_DIR):
    """
    Backup production or development
    """

    ENVIRONMENT = get_environment()

    # Don't do anything if the environment is not production
    if ENVIRONMENT == "production":
        backup_prod(BASE_DIR)
    else:
        backup_dev(BASE_DIR)

def setup(BASE_DIR):
    """
    Setup logging, environment variables
    and django
    """

    logging.basicConfig(
        level=logging.INFO,
        # display time in log messages
        format='[%(asctime)s] %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p'
    )

    setup_django(BASE_DIR)

    # Read environment files
    env = read_env(BASE_DIR)

    return env

if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

    setup(BASE_DIR)

    # backup the database
    backup(BASE_DIR)

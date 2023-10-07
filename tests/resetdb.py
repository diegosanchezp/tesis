import unittest
import os

from shscripts.reset_db import (
    create_connection,
    loaddata,
)

from shscripts.backup import (
    read_env, setup_django, backup,
    get_fixture_path, get_fixture_meta,
    get_fixture_folder,
)

from pathlib import Path

# python -m unittest tests.resetdb.TestReset.test_backup_prod

class TestReset(unittest.TestCase):
    def setUp(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file
        self.env = read_env(self.BASE_DIR)
        self.connection = create_connection(self.env)
        setup_django(self.BASE_DIR)

    def test_backup_prod(self):
        os.environ.setdefault("ENVIRONMENT", "production")
        backup(self.BASE_DIR)

        FIXTURE_PATH = get_fixture_path(self.BASE_DIR)

        self.assertTrue(FIXTURE_PATH.exists(), msg=f"{FIXTURE_PATH} folder doesn't exists")

        try:
            get_fixture_meta(self.BASE_DIR)
        except OSError:
            # Test failed
            self.fail("fixture meta file doesn't exists")
    def test_loaddata(self):
        os.environ.setdefault("ENVIRONMENT", "production")
        loaddata(self.BASE_DIR)

    def test_backup_dev(self):
        os.environ.setdefault("ENVIRONMENT", "development")

        backup_folder = get_fixture_folder(self.BASE_DIR)

        wagtail_fixture = backup_folder / "wagtail_pages.json"

        # Remove the wagtail fixture
        wagtail_fixture.unlink()

        # Make back again the wagtail fixture
        backup(self.BASE_DIR)

        self.assertTrue(wagtail_fixture.exists)


    def tearDown(self):
        self.connection.close()

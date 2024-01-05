# Core python libs
from pathlib import Path
import os
import unittest
import environ

from shscripts.backup import (
    setup_django,
)

from storages.backends.s3 import S3Storage
from django.core.files.storage import storages

class TestStorages(unittest.TestCase):

    def setUp(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

        os.environ["DJANGO_SETTINGS_MODULE"] = "django_src.settings.production"

        env = environ.Env()

        ENV_DIR = self.BASE_DIR / "envs" / "production"  # noqa F405
        env.read_env(str(ENV_DIR / "django"))  # noqa F405
        env.read_env(str(ENV_DIR / "postgres"))  # noqa F405
        setup_django(self.BASE_DIR, DJANGO_SETTINGS_MODULE="django_src.settings.production")

    # python -m unittest tests.storages.TestStorages.test_s3_storage
    def test_s3_storage(self):
        self.assertEqual(os.getenv("DJANGO_SETTINGS_MODULE"), "django_src.settings.production")
        s3_storage = storages["default"]
        self.assertTrue(isinstance(s3_storage, S3Storage))
        file = s3_storage.open(name="student_vouchers/profile_pic.jpg")
        self.assertIsNotNone(file)
        breakpoint()


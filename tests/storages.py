# Core python libs
from pathlib import Path
import os
import unittest
import environ

from shscripts.backup import (
    setup_django,
)

from storages.backends.s3 import S3Storage, S3File
from django.core.files.storage import storages
from django.conf import settings

"""
docker run --rm \
--env-file ./envs/production/django \
--env-file ./envs/production/postgres \
--env DJANGO_SETTINGS_MODULE=django_src.settings.production \
--mount 'type=bind,source=./tests,destination=/app/tests' \
--mount 'type=bind,source=./django_src,destination=/app/django_src' \
--network production_default \
--interactive --tty \
"$DOCKER_IMAGE" \
python -m unittest tests.storages.TestStorages.test_s3_storage
"""

class TestStorages(unittest.TestCase):

    def setUp(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

        setup_django(self.BASE_DIR, DJANGO_SETTINGS_MODULE="django_src.settings.production")
        from django_src.apps.main.models import HomePage
        self.HomePage = HomePage

    # python -m unittest tests.storages.TestStorages.test_s3_storage
    def test_s3_storage(self):
        self.assertEqual(os.getenv("DJANGO_SETTINGS_MODULE"), "django_src.settings.production")
        s3_storage: S3Storage = storages["default"]
        self.assertTrue(isinstance(s3_storage, S3Storage))
        self.assertEqual(s3_storage.url_protocol, os.environ["AWS_S3_URL_PROTOCOL"])
        file: S3File = s3_storage.open(name="original_images/phone-mockup.png")
        self.assertIsNotNone(file)
        # Generate presigned url
        s3_storage.url(file.name)
        home_page = self.HomePage.objects.first()
        home_page.header_image.get_rendition("max-500x500").img_tag()
        breakpoint()


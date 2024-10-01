import unittest
from shscripts.backup import setup_django
from pathlib import Path
import boto3
import os
import requests

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
python -m unittest tests.prod_bucket.TestProdBucket.test_s3_access
"""

# python -m unittest tests.prod_bucket.TestProdBucket
class TestProdBucket(unittest.TestCase):
    def setUp(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

        setup_django(self.BASE_DIR, DJANGO_SETTINGS_MODULE="django_src.settings.production")

    # python -m unittest tests.prod_bucket.TestProdBucket.test_s3_access
    def test_s3_access(self):
        """
        Test the permission policies of the S3 bucket
        """
        s3_resource = boto3.resource('s3')
        bucket_name = os.environ["AWS_STORAGE_BUCKET_NAME"]
        bucket_base_url = f"https://{bucket_name}.s3.amazonaws.com"
        bucket = s3_resource.Bucket(bucket_name)

        logo_egresados_name = "logo_egresados_ucv.jpg"
        logo_egresados_static_key = f"static/{logo_egresados_name}"
        logos_path = self.BASE_DIR / "static" / "img" / logo_egresados_name

        # As the django user, I can upload files to the bucket
        bucket.upload_file(Filename=logos_path.resolve(), Key=logo_egresados_static_key)

        # Anyone can read files on /static folder
        logo_res = requests.get(f"{bucket_base_url}/{logo_egresados_static_key}")
        self.assertEqual(logo_res.status_code, 200)

        # Shouldn't be able to read files on root folders
        logos_root_key = logo_egresados_name
        bucket.upload_file(Filename=logos_path.resolve(), Key=logos_root_key)
        logo_res = requests.get(f"{bucket_base_url}/{logos_root_key}")
        self.assertEqual(logo_res.status_code, 403)

        # Should not be able to write to the bucket
        # requests.post(f"")

        # Todo public_media
        # Clean up
        s3_response = bucket.delete_objects(
            Delete={
                'Objects': [
                    {
                        'Key': logo_egresados_static_key,
                    },
                    {
                        'Key': logos_root_key,
                    },
                ],
                'Quiet': False
            },
        )
        print()
        self.assertEqual(s3_response["ResponseMetadata"]["HTTPStatusCode"], 200, msg=s3_response)
        print(s3_response["Deleted"])



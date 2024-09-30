import os
from pathlib import Path
import unittest
from storages.backends.s3 import S3Storage
import boto3

class TestLocalStack(unittest.TestCase):
    def setUp(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file

    # python -m unittest tests.localstack.TestLocalStack.test_s3_storage
    def test_s3_storage(self):

        # read a file in ../static/img/logo_egresados_ucv.jpg and upload it to the bucket
        # using the S3Storage class from django-storages
        s3storage = S3Storage()
        s3resource = s3storage.connection
        session = s3storage._create_session()
        bucket = s3storage.bucket
        settings = s3storage.get_default_settings()
        breakpoint()
        self.assertEquals(settings['AWS_S3_REGION_NAME'], os.environ['AWS_S3_REGION_NAME'])
        print()




        # with open(self.BASE_DIR / 'static/img/logo_egresados_ucv.jpg', 'rb') as f:
        #     client.upload_fileobj(f, os.environ['AWS_STORAGE_BUCKET_NAME'], 'img/logo_egresados_ucv.jpg')

    def test_boto3(self):
        print(self.BASE_DIR)
        client = boto3.client('s3', endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"])
        response = client.list_buckets()
        print(response['Buckets'])
        # read a file in ../static/img/logo_egresados_ucv.jpg and upload it to the bucket
        # with open(self.BASE_DIR / 'static/img/logo_egresados_ucv.jpg', 'rb') as f:
        #     client.upload_fileobj(f, os.environ['AWS_STORAGE_BUCKET_NAME'], 'img/logo_egresados_ucv.jpg')

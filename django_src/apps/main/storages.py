from storages.backends.s3boto3 import S3StaticStorage

class StaticStorage(S3StaticStorage):
    location = "static"
    # default_acl = "public-read"

class MediaStorage(S3StaticStorage):

    # path prefix that will be prepended to all uploads
    location = "media"

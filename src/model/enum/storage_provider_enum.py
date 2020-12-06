from enum import Enum


class StorageProvider(Enum):
    FS = "fs"
    S3 = "s3"
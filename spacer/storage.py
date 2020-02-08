import abc
import boto
import os
from io import BytesIO
from PIL import Image
from spacer import config
from typing import Union, Tuple


class Storage(abc.ABC):

    @abc.abstractmethod
    def load_image(self, key) -> Image:
        pass

    @abc.abstractmethod
    def store_string(self, content: str, keyname: str) -> None:
        pass

    @abc.abstractmethod
    def load_string(self, content: str, keyname: str) -> str:
        pass


class S3Storage(Storage):

    def __init__(self, bucketname: str):

        conn = boto.connect_s3()
        self.bucket = conn.get_bucket(bucketname, validate=True)

    def load_image(self, keyname) -> Image:

        key = self.bucket.get_key(keyname)
        return Image.open(BytesIO(key.get_contents_as_string()))

    def store_string(self, content: str, keyname: str):

        key = self.bucket.get_key(keyname)
        key.set_contents_from_string(content)

    def load_string(self, content: str, keyname: str):
        key = self.bucket.get_key(keyname)
        return key.get_contents_as_string()


class LocalStorage(Storage):

    def __init__(self):
        pass

    def load_image(self, path) -> Image:
        return Image.open(path)

    def store_string(self, content: str, keyname: str):
        with open(keyname, 'w') as f:
            f.write(content)

    def load_string(self, content: str, keyname: str):
        with open(keyname, 'r') as f:
            return f.read()


def storage_factory(storage_type: str, bucketname: Union[str, None]):

    assert storage_type in config.STORAGE_TYPES

    if storage_type == 's3':
        return S3Storage(bucketname=bucketname)
    elif storage_type == 'local':
        return LocalStorage()
    else:
        raise ValueError('Unknown storage type: {}'.format(storage_type))


def download_model(keyname: str) -> Tuple[str, bool]:
    """ Utility method to download model with to local cache. """

    destination = os.path.join(config.LOCAL_MODEL_PATH, keyname)
    if not os.path.isfile(destination):
        print("downloading {}".format(keyname))
        conn = boto.connect_s3()
        bucket = conn.get_bucket(config.MODELS_BUCKET, validate=True)
        key = bucket.get_key(keyname)
        key.get_contents_to_filename(destination)
        was_cashed = False
    else:
        # Already cached, no need to download
        was_cashed = True

    return destination, was_cashed

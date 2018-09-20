import base64
from typing import BinaryIO


def encode_file(file: BinaryIO) -> str:
    byte_stream = getattr(file, 'getvalue', file.read)()
    encoded = base64.b64encode(byte_stream)
    return encoded.decode('utf-8')


def get_uuid(resource: dict) -> str:
    return resource['url'].rsplit('/')[-1]

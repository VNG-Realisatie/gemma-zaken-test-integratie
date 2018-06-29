import os
from io import BytesIO

from django.core.files import File

import pytest
from PIL import Image


@pytest.fixture
def text_file(request):
    """
        Generates a temporary '.txt' file.
        Returns file as a 'BufferedReader'
        Use .read() function to get file content as bytes.
    """

    PATH = 'dummy.txt'
    with open(PATH, 'w') as tmp:
        tmp.write('some additional information')
    data = open(PATH, 'rb')

    def fin():
        data.close()
        os.remove(PATH)

    request.addfinalizer(fin)
    return data


@pytest.fixture
def png_file(request):
    """
        Generates a temporary '.png' image.
        Returns file as a 'BytesIO'
        Use .getvalue() function to get image content as bytes.
    """

    im_format = 'png'
    im = Image.new('RGB', (1, 1), 'blue') # only 1 blue pixel
    buffered = BytesIO()
    im.save(buffered, format=im_format)
    return buffered

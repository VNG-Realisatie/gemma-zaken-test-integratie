import os
from io import BytesIO

from django.core.files import File

import pytest
from PIL import Image


@pytest.fixture
def text_file(request):
    PATH = 'dummy.txt'
    with open(PATH, 'w') as tmp:
        tmp.write('some additional information')

    def fin():
        os.remove(PATH)

    request.addfinalizer(fin)
    return open(PATH, 'rb')


@pytest.fixture
def png_file(request):
    im_format = 'png'
    im = Image.new('RGB', (512, 512), 'blue') # plain blue square
    buffered = BytesIO()
    im.save(buffered, format=im_format)
    return buffered

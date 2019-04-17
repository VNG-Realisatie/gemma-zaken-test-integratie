import os
from io import BytesIO

import pytest
from PIL import Image
from zds_client import Client

from .constants import BASE_DIR

CONFIG_FILE = os.path.join(BASE_DIR, 'config.yml')

Client.load_config(CONFIG_FILE)

_zrc_client = Client('zrc')
_drc_client = Client('drc')
_ztc_client = Client('ztc')
_brc_client = Client('brc')
_orc_client = Client('orc')
_nc_client = Client('nc')


@pytest.fixture
def text_file(request):
    """
    Generate a temporary '.txt' file.

    Returns file as a file opened in binary read mode.
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
    Generate a temporary '.png' image.

    Returns file as a 'BytesIO' object.
    Use .getvalue() to get image content as bytes.
    """
    im_format = 'png'
    im = Image.new('RGB', (1, 1), 'blue')  # only 1 blue pixel
    buffered = BytesIO()
    im.save(buffered, format=im_format)
    return buffered


@pytest.fixture
def zrc_client():
    # reset auth between tests
    if hasattr(_zrc_client.auth, '_credentials'):
        claims = _zrc_client._config.auth.claims.copy()
        _zrc_client.auth.claims = claims
        del _zrc_client.auth._credentials
    return _zrc_client


@pytest.fixture
def drc_client():
    # reset auth between tests
    if hasattr(_drc_client.auth, '_credentials'):
        claims = _drc_client._config.auth.claims.copy()
        _drc_client.auth.claims = claims
        del _drc_client.auth._credentials
    return _drc_client


@pytest.fixture
def ztc_client():
    # reset auth between tests
    if hasattr(_ztc_client.auth, '_credentials'):
        claims = _ztc_client._config.auth.claims.copy()
        _ztc_client.auth.claims = claims
        del _ztc_client.auth._credentials
    return _ztc_client


@pytest.fixture
def brc_client():
    # reset auth between tests
    if hasattr(_brc_client.auth, '_credentials'):
        claims = _brc_client._config.auth.claims.copy()
        _brc_client.auth.claims = claims
        del _brc_client.auth._credentials
    return _brc_client


@pytest.fixture
def orc_client():
    # reset auth between tests
    if hasattr(_orc_client.auth, '_credentials'):
        claims = _orc_client._config.auth.claims.copy()
        _orc_client.auth.claims = claims
        del _orc_client.auth._credentials
    return _orc_client


@pytest.fixture
def nc_client():
    # reset auth between tests
    if hasattr(_nc_client.auth, '_credentials'):
        claims = _nc_client._config.auth.claims.copy()
        _nc_client.auth.claims = claims
        del _nc_client.auth._credentials
    return _nc_client


class State(dict):
    def __setattr__(self, attr, value):
        self[attr] = value

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as exc:
            raise AttributeError from exc


@pytest.fixture(scope='session')
def state() -> State:
    return State()


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)

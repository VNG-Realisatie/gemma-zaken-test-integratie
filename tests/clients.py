import os

from zds_client import Client


BASE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
))

CONFIG_FILE = os.path.join(BASE_DIR, 'config.yml')

Client.load_config(CONFIG_FILE)

ztc_client = Client('ztc')
zrc_client = Client('zrc')
orc_client = Client('orc')
drc_client = Client('drc')

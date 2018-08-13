import os

from zds_client import Client


BASE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
))

CONFIG_FILE = os.path.join(BASE_DIR, 'config.yml')

Client.load_config(BASE_DIR, CONFIG_FILE)

zrc_client = Client('zrc')
drc_client = Client('drc')
ztc_client = Client('ztc')
orc_client = Client('orc')

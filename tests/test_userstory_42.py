"""
Assert that we can query on geometry
"""
import json
import os

from .constants import BASE_DIR, CATALOGUS_UUID, ZAAKTYPE_UUID

ANDER_ZAAKTYPE_UUID = '42e85d1e-f3fd-40be-b39a-72b67f73ea8d'


def test_opvragen_zaken_binnen_geometrie(zrc_client, ztc_client):
    geo_file = os.path.join(BASE_DIR, 'tests', 'geo', 'amsterdam_centrum.json')
    with open(geo_file, 'r') as infile:
        amsterdam_centrum = json.load(infile)

    zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
    zaaktype2 = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ANDER_ZAAKTYPE_UUID)

    # create zaak-objects
    zaak1 = zrc_client.create('zaak', {
        'zaaktype': zaaktype['url'],
        'bronorganisatie': '517439943',
        'startdatum': '2018-06-18',
        'registratiedatum': '2018-06-18',
    })
    zaak2 = zrc_client.create('zaak', {
        'zaaktype': zaaktype['url'],
        'bronorganisatie': '517439943',
        'startdatum': '2018-08-13',
        'registratiedatum': '2018-08-13',
        'zaakgeometrie': {
            'type': 'Point',
            'coordinates': [
                4.8855282,
                52.3766712
            ]
        }
    })
    zaak3 = zrc_client.create('zaak', {
        'zaaktype': zaaktype2['url'],
        'bronorganisatie': '517439943',
        'startdatum': '2018-08-13',
        'registratiedatum': '2018-08-13',
        'zaakgeometrie': {
            'type': 'Point',
            'coordinates': [
                4.8855282,
                52.3766712
            ]
        }
    })

    # perform the call
    zoek_result = zrc_client.operation('zaak__zoek', {
        'zaaktype': zaaktype['url'],
        'zaakgeometrie': {
            'within': amsterdam_centrum
        }
    })

    result_urls = [zaak['url'] for zaak in zoek_result]

    assert zaak1['url'] not in result_urls
    assert zaak2['url'] in result_urls
    assert zaak3['url'] not in result_urls

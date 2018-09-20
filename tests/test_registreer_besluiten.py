"""
Test dat het mogelijk is om BESLUITen toe te kennen aan ZAAKen, die vastgelegd
zijn in (een) INFORMATIEOBJECT(en).
"""
import pytest
import requests

from .constants import (
    CATALOGUS_UUID, INFORMATIEOBJECTTYPE_UUID, ZAAKTYPE_UUID, BESLUITTYPE_UUID
)
from .utils import encode_file


def _get_uuid(resource: dict) -> str:
    return resource['url'].rsplit('/')[-1]


@pytest.mark.incremental
class TestBesluiten:

    def test_creeer_zaak(self, state, zrc_client, ztc_client):
        zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
        state.zaaktype = zaaktype

        zaak = zrc_client.create('zaak', {
            'zaaktype': zaaktype['url'],
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': 'https://example.com/een_organisatie',
            'startdatum': '2018-06-18',
        })

        assert 'url' in zaak
        state.zaak = zaak

    def test_creeer_besluit(self, state, ztc_client, brc_client):
        besluittype = ztc_client.retrieve('besluittype', catalogus_uuid=CATALOGUS_UUID, uuid=BESLUITTYPE_UUID)
        assert 'url' in besluittype

        besluit = brc_client.create('besluit', {
            'verantwoordelijkeOrganisatie': '517439943',
            'besluittype': besluittype['url'],
            'datum': '2018-09-12T14:46:26+0200',
            'ingangsdatum': '2018-09-13',
            'zaak': state.zaak['url'],
        })

        assert 'url' in besluit
        state.besluit = besluit

    def test_leg_besluit_vast_in_informatieobject(self, state, text_file, drc_client, ztc_client):
        informatieobjecttype = ztc_client.retrieve(
            'informatieobjecttype',
            catalogus_uuid=CATALOGUS_UUID,
            uuid=INFORMATIEOBJECTTYPE_UUID
        )
        assert 'url' in informatieobjecttype

        document = drc_client.create('enkelvoudiginformatieobject', {
            'creatiedatum': '2018-09-12',
            'titel': 'besluit.txt',
            'auteur': 'Jos den Homeros',
            'taal': 'dut',
            'informatieobjecttype': informatieobjecttype['url'],
            'inhoud': encode_file(text_file),
        })
        assert 'url' in document
        state.document = document

        oio = drc_client.create('objectinformatieobject', {
            'informatieobject': document['url'],
            'object': state.besluit['url'],
            'objectType': 'besluit',
            'registratiedatum': '2018-09-12T16:25:36+0200',
        })

        assert 'url' in oio

    def test_opvragen_gegevens(self, state, zrc_client, brc_client, drc_client):
        # alle besluiten bij een zaak...
        besluiten = brc_client.list('besluit', query_params={'zaak': state.zaak['url']})
        assert len(besluiten) == 1

        # alle informatieobjecten bij een zaak...
        zaak_uuid = _get_uuid(state.zaak)
        zaakinformatieobjecten = zrc_client.list('zaakinformatieobject', zaak_uuid=zaak_uuid)
        assert len(zaakinformatieobjecten) == 0

        # besluitinformatieobjecten -> DRC MOET deze syncen naar BRC
        besluit_uuid = _get_uuid(state.besluit)
        besluitinformatieobjecten = brc_client.list('besluitinformatieobject', besluit_uuid=besluit_uuid)
        assert len(besluitinformatieobjecten) == 1

        informatieobject_url = besluitinformatieobjecten[0]['informatieobject']
        assert informatieobject_url == state.document['url']
        response = requests.get(informatieobject_url)
        assert response.status_code == 200

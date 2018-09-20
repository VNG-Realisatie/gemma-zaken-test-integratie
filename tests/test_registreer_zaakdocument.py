"""
Test dat het mogelijk is om een informatieobject slechts eenmalig te relateren
aan een zaak.
"""
import pytest
import requests

from .constants import CATALOGUS_UUID, INFORMATIEOBJECTTYPE_UUID, ZAAKTYPE_UUID
from .utils import encode_file, get_uuid


class TestZaakInformatieObjecten:

    def test_creeer_zaak_en_informatieobject(self, state, zrc_client, drc_client, ztc_client, text_file):
        # aanmaken zaak
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

        # aanmaken informatieobject
        informatieobjecttype = ztc_client.retrieve(
            'informatieobjecttype',
            catalogus_uuid=CATALOGUS_UUID,
            uuid=INFORMATIEOBJECTTYPE_UUID
        )
        assert 'url' in informatieobjecttype
        state.informatieobjecttype = informatieobjecttype

        document = drc_client.create('enkelvoudiginformatieobject', {
            'creatiedatum': '2018-09-12',
            'titel': 'zaak_samenvatting.txt',
            'auteur': 'Jos den Homeros',
            'taal': 'dut',
            'informatieobjecttype': informatieobjecttype['url'],
            'inhoud': encode_file(text_file),
        })
        assert 'url' in document
        state.document = document

    def test_relateer_zaak_en_informatieobject(self, state, zrc_client, drc_client):
        oio = drc_client.create('objectinformatieobject', {
            'informatieobject': state.document['url'],
            'object': state.zaak['url'],
            'objectType': 'zaak',
            'registratiedatum': '2018-09-12T16:25:36+0200',
        })

        assert 'url' in oio

        # tweede keer zelfde document mag niet!
        with pytest.raises(requests.HTTPError) as exc_context:
            drc_client.create('objectinformatieobject', {
                'informatieobject': state.document['url'],
                'object': state.zaak['url'],
                'objectType': 'zaak',
                'registratiedatum': '2018-09-12T16:25:59+0200',
            })

        assert exc_context.value.response.status_code == 400

        # zaakinformatieobject moet bestaan in ZRC
        zaak_uuid = get_uuid(state.zaak)
        zaakinformatieobjecten = zrc_client.list('zaakinformatieobject', zaak_uuid=zaak_uuid)
        assert len(zaakinformatieobjecten) == 1

    def test_relateer_informatieobject_dubbel_zrc(self, state, zrc_client):
        """
        Test that the ZaakInformatieObject may not be duplicated in ZRC.

        This is to protect against unintended ZRC-side relation usage.
        """
        zaak_uuid = get_uuid(state.zaak)

        with pytest.raises(requests.HTTPError) as exc_context:
            zrc_client.create('zaakinformatieobject', {
                'informatieobject': state.document['url'],
            }, zaak_uuid=zaak_uuid)

        assert exc_context.value.response.status_code == 400

    def test_relatie_eerst_in_drc_dan_zrc(self, state, zrc_client, drc_client, text_file):
        """
        Test dat de relatie zaak-informatieobject moet bestaan in het DRC
        voordat je de symmetrische relatie in het ZRC mag leggen.
        """
        document2 = drc_client.create('enkelvoudiginformatieobject', {
            'creatiedatum': '2018-09-12',
            'titel': 'zaak_samenvatting.txt',
            'auteur': 'Jos den Homeros',
            'taal': 'dut',
            'informatieobjecttype': state.informatieobjecttype['url'],
            'inhoud': encode_file(text_file),
        })

        zaak_uuid = get_uuid(state.zaak)

        with pytest.raises(requests.HTTPError) as exc_context:
            zrc_client.create('zaakinformatieobject', {
                'informatieobject': document2['url'],
            }, zaak_uuid=zaak_uuid)

        assert exc_context.value.response.status_code == 400

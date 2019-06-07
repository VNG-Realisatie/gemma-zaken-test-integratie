"""
Test dat het mogelijk is om een informatieobject slechts eenmalig te relateren
aan een zaak.
"""
import pytest
from zds_client import ClientError

from .constants import CATALOGUS_UUID, INFORMATIEOBJECTTYPE_UUID, ZAAKTYPE_UUID
from .utils import encode_file, get_uuid


@pytest.mark.incremental
class TestZaakInformatieObjecten:

    def test_creeer_zaak_en_informatieobject(self, state, zrc_client, drc_client, ztc_client, text_file):
        # aanmaken zaak
        zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
        state.zaaktype = zaaktype

        zaak = zrc_client.create('zaak', {
            'zaaktype': zaaktype['url'],
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': '223122166',
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
            'bronorganisatie': '517439943',
            'titel': 'zaak_samenvatting.txt',
            'auteur': 'Jos den Homeros',
            'taal': 'dut',
            'informatieobjecttype': informatieobjecttype['url'],
            'inhoud': encode_file(text_file),
        })
        assert 'url' in document
        state.document = document

    def test_relateer_zaak_en_informatieobject(self, state, zrc_client, drc_client):
        zio = zrc_client.create('zaakinformatieobject', {
            'informatieobject': state.document['url'],
            'zaak': state.zaak['url'],
            'titel': 'some titel',
            'beschrijving': 'some beschrijving',
            'aardRelatieWeergave': 'hoort_bij'
        })

        assert 'url' in zio

        # tweede keer zelfde document mag niet!
        with pytest.raises(ClientError) as exc_context:
            zrc_client.create('zaakinformatieobject', {
                'informatieobject': state.document['url'],
                'zaak': state.zaak['url'],
                'titel': 'some titel',
                'beschrijving': 'some beschrijving',
                'aardRelatieWeergave': 'hoort_bij'
            })

        assert exc_context.value.args[0]['status'] == 400

        # objectinformatieobject exists in DRC
        oio = drc_client.list('objectinformatieobject', {'informatieobject': state.document['url']})
        assert len(oio) == 1

    def test_relateer_informatieobject_dubbel_drc(self, state, drc_client):
        """
        Test that the ObjectInformatieObject may not be duplicated in DRC.
        This is to protect against unintended DRC-side relation usage.
        """
        with pytest.raises(ClientError) as exc_context:
            drc_client.create('objectinformatieobject', {
                'informatieobject': state.document['url'],
                'object': state.zaak['url'],
                'objectType': 'zaak',
                'registratiedatum': '2018-09-19T16:25:36+0200',
            })

        assert exc_context.value.args[0]['status'] == 400

    def test_relatie_eerst_in_zrc_dan_drc(self, state, zrc_client, drc_client, text_file):
        """
        Test dat de relatie zaak-informatieobject moet bestaan in het ZRC
        voordat je de symmetrische relatie in het DRC mag leggen.
        """
        document2 = drc_client.create('enkelvoudiginformatieobject', {
            'creatiedatum': '2018-09-12',
            'bronorganisatie': '517439943',
            'titel': 'zaak_samenvatting.txt',
            'auteur': 'Jos den Homeros',
            'taal': 'dut',
            'informatieobjecttype': state.informatieobjecttype['url'],
            'inhoud': encode_file(text_file),
        })

        with pytest.raises(ClientError) as exc_context:
            result = drc_client.create('objectinformatieobject', {
                'informatieobject': document2['url'],
                'object': state.zaak['url'],
                'objectType': 'zaak',
                'registratiedatum': '2018-09-19T16:25:36+0200',
            })

        assert exc_context.value.args[0]['status'] == 400

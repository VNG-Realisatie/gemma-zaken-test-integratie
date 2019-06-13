"""
Test dat het mogelijk is om BESLUITen toe te kennen aan ZAAKen, die vastgelegd
zijn in (een) INFORMATIEOBJECT(en).
"""
import pytest
from zds_client import ClientError

from .constants import (
    BESLUITTYPE_UUID, CATALOGUS_UUID, INFORMATIEOBJECTTYPE_UUID, ZAAKTYPE_UUID
)
from .utils import encode_file


@pytest.mark.incremental
class TestBesluiten:

    def test_creeer_zaak(self, state, zrc_client, ztc_client):
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

    def test_creeer_besluit(self, state, ztc_client, brc_client):
        besluittype = ztc_client.retrieve('besluittype', catalogus_uuid=CATALOGUS_UUID, uuid=BESLUITTYPE_UUID)
        assert 'url' in besluittype

        besluit = brc_client.create('besluit', {
            'verantwoordelijkeOrganisatie': '517439943',
            'besluittype': besluittype['url'],
            'datum': '2018-09-12',
            'ingangsdatum': '2018-09-13',
            'zaak': state.zaak['url'],
        })

        assert 'url' in besluit
        state.besluit = besluit

    def test_leg_besluit_vast_in_informatieobject(self, state, text_file, drc_client, ztc_client, brc_client):
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
            'titel': 'besluit.txt',
            'auteur': 'Jos den Homeros',
            'taal': 'dut',
            'informatieobjecttype': informatieobjecttype['url'],
            'inhoud': encode_file(text_file),
        })
        assert 'url' in document
        state.document = document

        bio = brc_client.create('besluitinformatieobject', {
            'informatieobject': document['url'],
            'besluit': state.besluit['url'],
            'aard_relatie': 'hoort_bij',
        })

        assert 'url' in bio

    def test_uniciteit_besluitinformatieobject(self, state, brc_client):
        with pytest.raises(ClientError) as exc:
            brc_client.create('besluitinformatieobject', {
                'informatieobject': state.document['url'],
                'besluit': state.besluit['url'],
                'aard_relatie': 'hoort_bij',
            })

        assert exc.value.args[0]['status'] == 400

    def test_relateer_informatieobject_dubbel_brc(self, state, drc_client):
        """
        Test that the BesluitInformatieObject may not be duplicated in DRC.
        This is to protect against unintended DRC-side relation usage.
        """
        with pytest.raises(ClientError) as exc_context:
            drc_client.create('objectinformatieobject', {
                'informatieobject': state.document['url'],
                'object': state.besluit['url'],
                'objectType': 'besluit',
                'registratiedatum': '2018-09-19T16:25:36+0200',
            })

        assert exc_context.value.args[0]['status'] == 400

    def test_relatie_eerst_in_brc_dan_drc(self, state, drc_client, text_file):
        """
        Test dat de relatie besluit-informatieobject moet bestaan in het BRC
        voordat je de symmetrische relatie in het DRC mag leggen.
        """
        document2 = drc_client.create('enkelvoudiginformatieobject', {
            'creatiedatum': '2018-09-12',
            'bronorganisatie': '517439943',
            'titel': 'besluit.txt',
            'auteur': 'Jos den Homeros',
            'taal': 'dut',
            'informatieobjecttype': state.informatieobjecttype['url'],
            'inhoud': encode_file(text_file),
        })

        with pytest.raises(ClientError) as exc_context:
            drc_client.create('objectinformatieobject', {
                'informatieobject': document2['url'],
                'object': state.besluit['url'],
                'objectType': 'besluit',
                'registratiedatum': '2018-09-19T16:25:36+0200',
            })
        assert exc_context.value.args[0]['status'] == 400

    def test_opvragen_gegevens(self, state, zrc_client, brc_client, drc_client):
        # alle besluiten bij een zaak...
        besluiten = brc_client.list('besluit', query_params={'zaak': state.zaak['url']})
        assert len(besluiten) == 1

        # alle informatieobjecten bij een zaak...
        zaakinformatieobjecten = zrc_client.list('zaakinformatieobject', {'zaak': state.zaak['url']})
        assert len(zaakinformatieobjecten) == 0

        # besluitinformatieobjecten -> DRC MOET deze syncen naar BRC
        besluitinformatieobjecten = brc_client.list('besluitinformatieobject', {'besluit': state.besluit['url']})
        assert len(besluitinformatieobjecten) == 1

        informatieobject_url = besluitinformatieobjecten[0]['informatieobject']
        assert informatieobject_url == state.document['url']

        informatieobject = drc_client.retrieve('enkelvoudiginformatieobjecten', informatieobject_url)
        assert 'url' in informatieobject

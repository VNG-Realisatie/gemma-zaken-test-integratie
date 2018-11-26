"""
Test dat het afsluiten van een ZAAK werkt via het zetten van een eindstatus.
"""
import pytest

from .constants import (
    CATALOGUS_UUID, STATUSTYPE_2_UUID, STATUSTYPE_UUID, ZAAKTYPE_UUID
)


@pytest.mark.incremental
class TestZaakAfsluiten:

    def test_creeer_zaak(self, state, zrc_client, ztc_client):
        zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
        state.zaaktype = zaaktype

        zaak = zrc_client.create('zaak', {
            'zaaktype': zaaktype['url'],
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': 'https://example.com/een_organisatie',
            'startdatum': '2018-10-01',
        })

        assert 'url' in zaak
        assert zaak['einddatum'] is None
        assert zaak['status'] is None
        state.zaak = zaak

    def test_zet_initiele_status(self, state, zrc_client, ztc_client):
        statustype = ztc_client.retrieve(
            'statustype', catalogus_uuid=CATALOGUS_UUID,
            zaaktype_uuid=ZAAKTYPE_UUID, uuid=STATUSTYPE_UUID
        )

        assert statustype['volgnummer'] == 1
        assert statustype['isEindstatus'] is False
        state.statustype_1 = statustype

        status = zrc_client.create('status', {
            'zaak': state.zaak['url'],
            'statusType': statustype['url'],
            'datumStatusGezet': '2018-10-01T10:00:00Z',
        })

        assert 'url' in status
        state.status_1 = status

        zaak = zrc_client.retrieve('zaak', uuid=state.zaak['uuid'])
        assert zaak['einddatum'] is None
        assert zaak['status'] == status['url']
        state.zaak = zaak

    def test_zet_eind_status(self, state, zrc_client, ztc_client):
        statustype = ztc_client.retrieve(
            'statustype', catalogus_uuid=CATALOGUS_UUID,
            zaaktype_uuid=ZAAKTYPE_UUID, uuid=STATUSTYPE_2_UUID
        )

        assert statustype['volgnummer'] == 2
        assert statustype['isEindstatus'] is True
        state.statustype_2 = statustype

        status = zrc_client.create('status', {
            'zaak': state.zaak['url'],
            'statusType': statustype['url'],
            'datumStatusGezet': '2018-10-18T20:00:00Z',
        })

        assert 'url' in status
        state.status_2 = status

        zaak = zrc_client.retrieve('zaak', uuid=state.zaak['uuid'])
        assert zaak['einddatum'] == '2018-10-18'
        assert zaak['status'] == status['url']
        state.zaak = zaak

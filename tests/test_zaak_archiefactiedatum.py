"""
Test archive procedure of Zaak:
purpose: to test calculation of Zaak.archiefactiedatum
In this testcase we check case when Zaak.archiefactiedatum = brondatum of Zaak + ResultaatType.archiefactietermijn
"""
import pytest

from .constants import (
    CATALOGUS_UUID, RESULTAATTYPE_UUID, STATUSTYPE_2_UUID, ZAAKTYPE_UUID
)


@pytest.mark.incremental
class TestZaakArchiefactiedatum:

    def test_create_zaak(self, state, zrc_client, ztc_client):
        zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
        state.zaaktype = zaaktype

        zrc_client.auth.set_claims(
            scopes=['zds.scopes.zaken.aanmaken'],
            zaaktypes=[zaaktype['url']]
        )

        zaak = zrc_client.create('zaak', {
            'zaaktype': zaaktype['url'],
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': '223122166',
            'startdatum': '2018-06-01',
            'registratiedatum': '2018-06-18',
        })

        assert 'url' in zaak
        assert zaak['archiefactiedatum'] is None
        state.zaak = zaak

    def test_create_resultaat(self, state, zrc_client, ztc_client):
        zrc_client.auth.set_claims(
            scopes=[
                'zds.scopes.zaken.lezen',
                'zds.scopes.zaken.bijwerken'
            ],
            zaaktypes=[state.zaaktype['url']]
        )
        resultaattype = ztc_client.retrieve('resultaattype', uuid=RESULTAATTYPE_UUID)

        assert 'url' in resultaattype

        resultaat = zrc_client.create('resultaat', {
            'zaak': state.zaak['url'],
            'resultaatType': resultaattype['url'],
            'toelichting': 'Een toelichting op wat het resultaat',
        })

        assert 'url' in resultaat

    def test_create_status(self, state, zrc_client, ztc_client):
        """
        to calculate archiefactiedatum we need zaak brondatum
        to calculate zaak brondatum we need zaak object to have einddatum not Null
        zaak.einddatum is read-only object, therefore we need to create status to change it
        """
        zrc_client.auth.set_claims(
            scopes=[
                'zds.scopes.zaken.lezen',
                'zds.scopes.statussen.toevoegen'
            ],
            zaaktypes=[state.zaaktype['url']]
        )

        statustype = ztc_client.retrieve(
            'statustype', catalogus_uuid=CATALOGUS_UUID,
            zaaktype_uuid=ZAAKTYPE_UUID, uuid=STATUSTYPE_2_UUID
        )

        assert statustype['isEindstatus'] is True
        state.statustype = statustype

        status = zrc_client.create('status', {
            'zaak': state.zaak['url'],
            'statusType': statustype['url'],
            'datumStatusGezet': '2018-10-18T20:00:00Z',
        })

        assert 'url' in status
        state.status = status

        zaak = zrc_client.retrieve('zaak', url=state.zaak['url'])

        assert zaak['einddatum'] == '2018-10-18'
        assert zaak['archiefactiedatum'] == '2018-11-17'

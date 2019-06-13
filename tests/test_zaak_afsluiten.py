"""
Test dat het afsluiten van een ZAAK werkt via het zetten van een eindstatus.
"""
import pytest
from zds_client import ClientError

from .constants import (
    CATALOGUS_UUID, INFORMATIEOBJECTTYPE_UUID, RESULTAATTYPE_UUID,
    STATUSTYPE_2_UUID, STATUSTYPE_UUID, ZAAKTYPE_UUID
)
from .utils import encode_file, get_uuid


@pytest.mark.incremental
class TestZaakAfsluiten:

    def test_creeer_zaak(self, state, zrc_client, ztc_client):
        zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
        state.zaaktype = zaaktype

        zaak = zrc_client.create('zaak', {
            'zaaktype': zaaktype['url'],
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': '223122166',
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

        zaak = zrc_client.retrieve('zaak', url=state.zaak['url'])

        assert zaak['einddatum'] is None
        assert zaak['status'] == status['url']
        state.zaak = zaak

    def test_zet_resultaat(self, state, zrc_client, ztc_client):
        """
        A resultaat is needed before you can close the case.
        """
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

    def test_zet_eind_status(self, state, zrc_client, ztc_client):
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

        zaak = zrc_client.retrieve('zaak', url=state.zaak['url'])

        assert zaak['einddatum'] == '2018-10-18'
        assert zaak['status'] == status['url']
        state.zaak = zaak


@pytest.mark.incremental
class TestZaakAfsluitenMetInformatieObjecten:

    def test_creeer_zaak_en_ios(self, state, zrc_client, drc_client, ztc_client, text_file):
        zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
        state.zaaktype = zaaktype

        zaak = zrc_client.create('zaak', {
            'zaaktype': zaaktype['url'],
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': '223122166',
            'startdatum': '2018-10-01',
        })

        assert 'url' in zaak
        assert zaak['einddatum'] is None
        assert zaak['status'] is None
        state.zaak = zaak

        # aanmaken informatieobjecten
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
            'indicatieGebruiksrecht': None,
        })
        assert 'url' in document
        state.document = document

        # relateer zaak en io
        zio = zrc_client.create('zaakinformatieobject', {
            'informatieobject': state.document['url'],
            'zaak': state.zaak['url'],
            'titel': 'some titel',
            'beschrijving': 'some beschrijving',
            'aardRelatieWeergave': 'hoort_bij'
        })
        assert 'url' in zio

    def test_zet_initiele_status(self, state, zrc_client, ztc_client):
        """
        Test dat een status anders dan de eindstatus zetten kan zonder de indicatie
        te zetten.
        """
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

    def test_zet_eind_status_validatiefout(self, state, zrc_client, ztc_client):
        statustype = ztc_client.retrieve(
            'statustype', catalogus_uuid=CATALOGUS_UUID,
            zaaktype_uuid=ZAAKTYPE_UUID, uuid=STATUSTYPE_2_UUID
        )

        assert statustype['volgnummer'] == 2
        assert statustype['isEindstatus'] is True
        state.statustype_2 = statustype

        with pytest.raises(ClientError) as exc_context:
            zrc_client.create('status', {
                'zaak': state.zaak['url'],
                'statusType': statustype['url'],
                'datumStatusGezet': '2018-10-18T20:00:00Z',
            })

        assert exc_context.value.args[0]['status'] == 400
        assert exc_context.value.args[0]['invalidParams'][0]['code'] == 'indicatiegebruiksrecht-unset'

    def test_zet_resultaat(self, state, zrc_client, ztc_client):
        """
        A resultaat is needed before you can close the case.
        """
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

    def test_update_indicatiegebruiksrecht(self, state, zrc_client, drc_client):
        document_lock = drc_client.request(
            f"{state.document['url']}/lock",
            'enkelvoudiginformatieobject_lock',
            method='POST'
        )

        document = drc_client.partial_update(
            'enkelvoudiginformatieobject',
            {'indicatieGebruiksrecht': False,
             'lock': document_lock['lock']},
            uuid=get_uuid(state.document)
        )
        assert document['indicatieGebruiksrecht'] is False
        state.document = document

        status = zrc_client.create('status', {
            'zaak': state.zaak['url'],
            'statusType': state.statustype_2['url'],
            'datumStatusGezet': '2018-10-18T20:00:00Z',
        })
        assert 'url' in status

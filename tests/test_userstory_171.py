"""
Test dat het mogelijk is om een document toe te voegen voor een zaak.

Ref: https://github.com/VNG-Realisatie/gemma-zaken/issues/171
"""
import base64

from .constants import CATALOGUS_UUID, INFORMATIEOBJECTTYPE_UUID, ZAAKTYPE_UUID


def test_upload_document(png_file, zrc_client, ztc_client, drc_client):
    zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
    zaak = zrc_client.create('zaak', {
        'zaaktype': zaaktype['url'],
        'bronorganisatie': '517439943',
        'verantwoordelijkeOrganisatie': 'https://example.com/een_organisatie',
        'startdatum': '2018-06-18',
    })

    informatieobjecttype = ztc_client.retrieve(
        'informatieobjecttype',
        catalogus_uuid=CATALOGUS_UUID,
        uuid=INFORMATIEOBJECTTYPE_UUID
    )

    # upload document in DRC
    byte_content = png_file.getvalue()
    base64_bytes = base64.b64encode(byte_content)

    document = drc_client.create('enkelvoudiginformatieobject', {
        'informatieobjecttype': informatieobjecttype['url'],
        'bronorganisatie': '517439943',
        'creatiedatum': zaak['registratiedatum'],
        'titel': 'afbeelding.png',
        'auteur': 'Jos den Homeros',
        'formaat': 'image/png',
        'taal': 'dut',
        'inhoud': base64_bytes.decode('utf-8')
    })

    assert 'identificatie' in document

    # relateer document aan zaak
    zio = drc_client.create('objectinformatieobject', {
        'informatieobject': document['url'],
        'object': zaak['url'],
        'objectType': 'zaak',
        'registratiedatum': '2018-09-19T16:25:36+0200'
    })

    assert 'url' in zio

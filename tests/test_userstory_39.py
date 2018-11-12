"""
Test that the various service reference implementations play well together.

Ref: https://github.com/VNG-Realisatie/gemma-zaken/issues/39
"""


import uuid
from base64 import b64encode

import requests

from .constants import (
    CATALOGUS_UUID, INFORMATIEOBJECTTYPE_UUID, STATUSTYPE_UUID, ZAAKTYPE_UUID
)


def test_melding_overlast(text_file, png_file, zrc_client, drc_client, ztc_client, orc_client):
    # retrieve zaaktype/statustype from ZTC
    zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
    status_type = ztc_client.retrieve(
        'statustype', catalogus_uuid=CATALOGUS_UUID,
        zaaktype_uuid=ZAAKTYPE_UUID, uuid=STATUSTYPE_UUID)

    assert status_type['url'] in zaaktype['statustypen']

    zrc_client.auth.set_claims(
        scopes=[
            'zds.scopes.zaken.aanmaken',
            'zds.scopes.zaken.lezen',
        ],
        zaaktypes=[zaaktype['url']]
    )

    # registreer zaak
    zaak = zrc_client.create('zaak', {
        'zaaktype': zaaktype['url'],
        'bronorganisatie': '517439943',
        'verantwoordelijkeOrganisatie': 'https://example.com/een_organisatie',
        'startdatum': '2018-06-18',
        'registratiedatum': '2018-06-18',
        'toelichting': 'Hout van een boot is afgebroken en blokkeert de '
                       'linkerdoorgang van een brug.',
        'zaakgeometrie': {
            'type': 'Point',
            'coordinates': [
                4.910649523925713,
                52.37240093589432
            ]
        }

    })
    zaak_uuid = zaak['url'].rsplit('/')[-1]
    assert 'url' in zaak

    # set status
    status = zrc_client.create('status', {
        'zaak': zaak['url'],
        'statusType': status_type['url'],
        'datumStatusGezet': '2018-06-18T15:11:33Z',
        'statustoelichting': 'Melding ontvangen',
    })

    zaak = zrc_client.retrieve('zaak', uuid=zaak_uuid)
    assert zaak['status'] == status['url']

    # assign address information
    verblijfsobject = orc_client.create('verblijfsobject', {
        'identificatie': uuid.uuid4().hex,
        'hoofdadres': {
            'straatnaam': 'Keizersgracht',
            'postcode': '1015 CJ',
            'woonplaatsnaam': 'Amsterdam',
            'huisnummer': '117',
        }
    })
    zaak_object = zrc_client.create('zaakobject', {
        'zaak': zaak['url'],
        'object': verblijfsobject['url'],
        'type': 'VerblijfsObject',
    })
    assert 'url' in zaak_object

    informatieobjecttype = ztc_client.retrieve(
        'informatieobjecttype',
        catalogus_uuid=CATALOGUS_UUID,
        uuid=INFORMATIEOBJECTTYPE_UUID
    )

    # Upload the files with POST /enkelvoudiginformatieobject (DRC)
    byte_content = text_file.read()  # text_file comes from pytest fixture
    base64_bytes = b64encode(byte_content)
    base64_string = base64_bytes.decode('utf-8')

    text_attachment = drc_client.create('enkelvoudiginformatieobject', {
        'identificatie': uuid.uuid4().hex,
        'informatieobjecttype': informatieobjecttype['url'],
        'bronorganisatie': '517439943',
        'creatiedatum': zaak['registratiedatum'],
        'titel': 'text_extra.txt',
        'auteur': 'anoniem',
        'formaat': 'text/plain',
        'taal': 'dut',
        'inhoud': base64_string
    })

    # Test if the EnkelvoudigInformatieObject stored has the right information
    assert 'creatiedatum' in text_attachment
    assert text_attachment['creatiedatum'] == zaak['registratiedatum']

    # Retrieve the EnkelvoudigInformatieObject
    txt_object_uuid = text_attachment['url'].rsplit('/')[-1]
    text_attachment = drc_client.retrieve('enkelvoudiginformatieobject', uuid=txt_object_uuid)

    # Test if the attached filed is our initial file
    assert requests.get(text_attachment['inhoud']).content == byte_content

    byte_content = png_file.getvalue()
    base64_bytes = b64encode(byte_content)
    base64_string = base64_bytes.decode('utf-8')

    image_attachment = drc_client.create('enkelvoudiginformatieobject', {
        'identificatie': uuid.uuid4().hex,
        'informatieobjecttype': informatieobjecttype['url'],
        'bronorganisatie': '517439943',
        'creatiedatum': zaak['registratiedatum'],
        'titel': 'afbeelding.png',
        'auteur': 'anoniem',
        'formaat': 'image/png',
        'taal': 'dut',
        'inhoud': base64_string
    })

    # Link the files to a 'Zaak' with POST /objectinformatieobjecten (ZRC)
    objectinformatieobject_1 = drc_client.create('objectinformatieobject', {
        'informatieobject': text_attachment['url'],
        'object': zaak['url'],
        'objectType': 'zaak',
        'registratiedatum': '2018-09-19T16:25:36+0200',
    })
    assert 'url' in objectinformatieobject_1

    objectinformatieobject_2 = drc_client.create('objectinformatieobject', {
        'informatieobject': image_attachment['url'],
        'object': zaak['url'],
        'objectType': 'zaak',
        'registratiedatum': '2018-09-19T16:25:36+0200',
    })
    informatie_object_uuid = objectinformatieobject_2['url'].rsplit('/')[-1]

    # Test if it's possible to retrieve ObjectInformatieObject
    some_informatie_object = drc_client.retrieve('objectinformatieobject', uuid=informatie_object_uuid)

    # Retrieve the EnkelvoudigInformatieObject from ObjectInformatieObject
    assert 'informatieobject' in some_informatie_object

    img_object_uuid = some_informatie_object['informatieobject'].rsplit('/')[-1]
    image_attachment = drc_client.retrieve('enkelvoudiginformatieobject', uuid=img_object_uuid)

    # Test if image correspond to our initial image
    assert requests.get(image_attachment['inhoud']).content == byte_content

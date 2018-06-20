"""
Test that the various service reference implementations play well together.

Ref: https://github.com/VNG-Realisatie/gemma-zaken/issues/39
"""
import uuid

import os, tempfile, base64
from PIL import Image
from io import BytesIO
import urllib.request

from zit.client import Client


def test_melding_overlast():
    ztc_client = Client('ztc')
    zrc_client = Client('zrc')
    orc_client = Client('orc')
    drc_client = Client('drc')

    # retrieve zaaktype/statustype from ZTC
    zaaktype = ztc_client.retrieve('zaaktype', catalogus_pk=1, id=1)
    status_type = ztc_client.retrieve('statustype', catalogus_pk=1, zaaktype_pk=1, id=1)
    assert status_type['url'] in zaaktype['statustypen']

    # registreer zaak
    zaak = zrc_client.create('zaak', {
        'zaaktype': zaaktype['url'],
        'registratiedatum': '2018-06-18',
        'toelichting': 'Hout van een boot is afgebroken en blokkeert de '
                       'linkerdoorgang van een brug.',
        'zaakgeometrie': 'POINT (4.910649523925713 52.37240093589432)',

    })
    zaak_id = zaak['url'].rsplit('/')[-1]
    assert 'url' in zaak

    # set status
    status = zrc_client.create('status', {
        'zaak': zaak['url'],
        'statusType': status_type['url'],
        'datumStatusGezet': '2018-06-18T15:11:33Z',
        'statustoelichting': 'Melding ontvangen',
    })

    zaak = zrc_client.retrieve('zaak', id=zaak_id)
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
    })
    assert 'url' in zaak_object


    '''
    Create temporary files to test file uploading
    '''
    # Text file (can't be empty or the API throws an error)
    fd, txt_path = tempfile.mkstemp()
    with open(txt_path, 'w') as tmp:
        tmp.write('some additional information')

    # Image (png format)
    im_format = 'png'
    im = Image.new('RGB', (512, 512), 'blue') #plain blue square
    buffered = BytesIO()
    im.save(buffered, format=im_format)

    '''
    Upload the files with POST /enkelvoudiginformatieobject (DRC)
    '''

    text_attachment = drc_client.create_form('enkelvoudiginformatieobject', {
    'identificatie': uuid.uuid4().hex,
    'bronorganisatie' : '1',
    'creatiedatum' : zaak['registratiedatum'],
    'titel' : 'detailed summary',
    'auteur' : 'test_auteur',
    'formaat' : 'txt',
    'taal' : 'english',
    }, {
        'inhoud': open(txt_path, 'rb')
    })

    # Test if the EnkelvoudigInformatieObject stored has the right information
    assert 'creatiedatum' in text_attachment
    assert text_attachment['creatiedatum'] == zaak['registratiedatum']

    # Retrieve the EnkelvoudigInformatieObject
    txt_object_id = text_attachment['url'].rsplit('/')[-1]
    text_attachment = drc_client.retrieve('enkelvoudiginformatieobject', id=txt_object_id)

    # Test if the attached filed is our initial file
    with open(txt_path, 'rb') as tmp:
        assert urllib.request.urlopen(text_attachment['inhoud']).read() == tmp.read()

    os.remove(txt_path) #remove the temporary file immediatly

    image_attachment = drc_client.create_form('enkelvoudiginformatieobject', {
    'identificatie': uuid.uuid4().hex,
    'bronorganisatie' : '1',
    'creatiedatum' : zaak['registratiedatum'],
    'titel' : 'attachment',
    'auteur' : 'test_auteur',
    'formaat' : im_format,
    'taal' : 'english',
    }, {
        'inhoud': buffered.getvalue()
    })

    '''
    Link the files to a 'Zaak' with POST /zaakinformatieobjecten (ZRC)
    '''

    ZaakInformatieObject_1 = zrc_client.create('zaakinformatieobject', {
        'zaak': zaak['url'],
        'informatieobject': text_attachment['url'],
    })

    ZaakInformatieObject_2 = zrc_client.create('zaakinformatieobject', {
        'zaak': zaak['url'],
        'informatieobject': image_attachment['url'],
    })

    informatie_object_id = ZaakInformatieObject_2['url'].rsplit('/')[-1]

    # Test if it's possible to retrieve ZaakInformatieObject
    some_informatie_object = zrc_client.retrieve('zaakinformatieobject', id=informatie_object_id)

    # Retrieve the EnkelvoudigInformatieObject from ZaakInformatieObject
    assert 'informatieobject' in some_informatie_object
    img_object_id = some_informatie_object['informatieobject'].rsplit('/')[-1]
    image_attachment = drc_client.retrieve('enkelvoudiginformatieobject', id=img_object_id)

    # Test if image correspond to our initial image
    assert urllib.request.urlopen(image_attachment['inhoud']).read() == buffered.getvalue()

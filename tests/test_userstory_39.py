"""
Test that the various service reference implementations play well together.

Ref: https://github.com/VNG-Realisatie/gemma-zaken/issues/39
"""
from zit.client import Client


def test_melding_overlast():
    ztc_client = Client('ztc')
    zrc_client = Client('zrc')

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

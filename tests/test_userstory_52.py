from zit.client import Client

CATALOGUS_UUID = '03a8a943-98aa-4e5a-8643-ad2d81db4d6b'
ZAAKTYPE_UUID = 'd1cb2212-0d9c-48fe-8a04-01317a9630f4'
STATUSTYPE_UUID = 'b7402827-8e7f-4081-ac24-7911b8929f97'


def find(collection, compare_func):
    for item in collection:
        if compare_func(item):
            return item
    raise Exception("Item not found")


def test_melding_eigenschappen():
    ztc_client = Client('ztc')
    zrc_client = Client('zrc')

    # retrieve zaaktype eigenschappen from ZTC
    zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
    eigenschappen = ztc_client.list('eigenschap', catalogus_uuid=CATALOGUS_UUID, zaaktype_uuid=ZAAKTYPE_UUID)
    eigenschap = find(eigenschappen, lambda item: item['naam'] == 'melding_type')
    assert eigenschap['specificatie']['waardenverzameling'][0] == 'water'

    # registreer zaak
    zaak = zrc_client.create('zaak', {
        'zaaktype': zaaktype['url'],
        'bronorganisatie': '517439943',
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
    assert zaak['zaakgeometrie'] == {
        'type': 'Point',
        'coordinates': [
            4.910649523925713,
            52.37240093589432
        ]
    }

    zaak_uuid = zaak['url'].rsplit('/')[-1]

    # registreer eigenschap
    zrc_client.create('zaakeigenschap', {
        'zaak': zaak['url'],
        'eigenschap': eigenschap['url'],
        'waarde': 'water'
    }, zaak_uuid=zaak_uuid)

    # lijst eigenschappen
    zaakeigenschappen = zrc_client.list('zaakeigenschap', zaak_uuid=zaak_uuid)
    assert len(zaakeigenschappen) == 1

    eigenschap = find(
        eigenschappen,
        lambda item: item['url'] == zaakeigenschappen[0]['eigenschap']
    )

    key_value_repr = f"{eigenschap['naam']}: {zaakeigenschappen[0]['waarde']}"
    assert key_value_repr == 'melding_type: water'

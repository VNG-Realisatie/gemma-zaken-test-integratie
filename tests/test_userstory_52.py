from zit.client import Client


def find(collection, compare_func):
    for item in collection:
        if compare_func(item):
            return item
    raise Exception("Item not found")


def test_melding_eigenschappen():
    ztc_client = Client('ztc')
    zrc_client = Client('zrc')

    # retrieve zaaktype eigenschappen from ZTC
    zaaktype = ztc_client.retrieve('zaaktype', catalogus_pk=1, id=1)
    eigenschappen = ztc_client.list('eigenschap', catalogus_pk=1, zaaktype_pk=1)
    eigenschap = find(eigenschappen, lambda item: item['naam'] == 'melding_type')
    assert eigenschap['specificatie']['waardenverzameling'][0] == 'water'

    # registreer zaak
    zaak = zrc_client.create('zaak', {
        'zaaktype': zaaktype['url'],
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

    zaak_id = zaak['url'].rsplit('/')[-1]

    # registreer eigenschap
    zrc_client.create('zaakeigenschap', {
        'zaak': zaak['url'],
        'eigenschap': eigenschap['url'],
        'waarde': 'water'
    }, zaak_pk=zaak_id)

    # lijst eigenschappen
    zaakeigenschappen = zrc_client.list('zaakeigenschap', zaak_pk=zaak_id)
    assert len(zaakeigenschappen) == 1

    eigenschap = find(
        eigenschappen,
        lambda item: item['url'] == zaakeigenschappen[0]['eigenschap']
    )

    key_value_repr = f"{eigenschap['naam']}: {zaakeigenschappen[0]['waarde']}"
    assert key_value_repr == 'melding_type: water'

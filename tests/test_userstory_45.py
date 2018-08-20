"""
Uit vng-Realisatie/gemma-zaken#169 en vng-Realisatie/gemma-zaken#45 blijkt dat
het mogelijk moet zijn om de behandelaar toe te wijzen aan een zaak.

Dit kan automatisch uit de zaaktypecatalogus (op basis van zaaktype), of
door een manuele actie van een KCC medewerker getriggered worden.
"""
from .constants import CATALOGUS_UUID, ZAAKTYPE_UUID


def test_zet_behandelaar_op_basis_van_zaaktype(zrc_client, ztc_client):
    # vraag zaaktype op
    zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)

    # maak een zaak aan
    zaak = zrc_client.create('zaak', {
        'zaaktype': zaaktype['url'],
        'bronorganisatie': '517439943',
        'startdatum': '2018-06-18',
        'registratiedatum': '2018-06-18',
    })
    assert 'url' in zaak

    # vraag behandelaar op
    roltypen = ztc_client.list(
        'roltype', catalogus_uuid=CATALOGUS_UUID, zaaktype_uuid=ZAAKTYPE_UUID,
        query_params={'omschrijvingGeneriek': 'Behandelaar'}
    )

    assert len(roltypen) == 1

    # zet de behandelaar
    behandelaar = roltypen[0]['mogelijkeBetrokkenen'][0]
    rol = zrc_client.create('rol', {
        'zaak': zaak['url'],
        'betrokkene': behandelaar['betrokkene'],
        'betrokkeneType': behandelaar['betrokkeneType'],
        'rolomschrijving': 'Behandelaar',
        'roltoelichting': 'Automatisch toegewezen op basis van zaaktype',
    })

    assert 'url' in rol

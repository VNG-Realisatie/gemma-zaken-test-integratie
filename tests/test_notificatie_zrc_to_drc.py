"""
Test whole notification process

1. producer side (zrc):
- registering kanaal
- sending notification

2. subscriver side (drc):
- subscribe to kanaal
- receive notification
"""
import pytest
from zds_client import ClientAuth

from .constants import CATALOGUS_UUID, ZAAKTYPE_UUID


@pytest.mark.incremental
class TestNotificatie:

    def test_zrc_create_kanaal(self, state, nrc_client):
        # can't run django command register_kanaal
        # therefore test Client.request under this command
        # check if kanaal exists - for local testing:
        kanaal_naam = 'zaken'
        kanalen = nrc_client.list('kanaal', query_params={'naam': kanaal_naam})

        if kanalen:
            kanaal = kanalen[0]
        else:
            kanaal = nrc_client.create('kanaal', {'naam': kanaal_naam})

        assert kanaal['naam'] == kanaal_naam
        assert 'url' in kanaal
        state.kanaal = kanaal

    def test_drc_subscriber_to_zaken_kanaal(self, state, nrc_client, drc_client):
        # can't add Subscription in the drc admin
        # therefore test Client.request under this command
        drc_auth = ClientAuth(
            client_id='demo',
            secret='demo',
        )

        # can't read url from spec, because it isn't added to schema
        # not working because /callbacks endpoint is not included in drc
        callback_url = '{}callbacks'.format(drc_client.base_url)

        data = {
            'callbackUrl': callback_url,
            'auth': drc_auth.credentials()['Authorization'],
            'kanalen': [{
                "naam": state.kanaal['naam'],
                "filters": {
                    "bronorganisatie": "517439943",
                    "zaaktype": "*",
                    "vertrouwelijkheidaanduiding": "*",
                }
            }],
        }

        # check if subscriber exists - for local testing:
        subs = [sub for sub in nrc_client.list('abonnement') if sub['callbackUrl'] == callback_url]

        if subs:
            subscriber = subs[0]
        else:
            subscriber = nrc_client.create('abonnement', data=data)

        assert 'url' in subscriber
        state.subscriber = subscriber

    def test_zrc_send_notif(self, state, zrc_client, ztc_client):
        """
        create Zaak object to send notification

        FIXME: get the notif config in ZRC correct so that it uses a proper,
        controlled NRC
        """
        zaaktype = ztc_client.retrieve('zaaktype', catalogus_uuid=CATALOGUS_UUID, uuid=ZAAKTYPE_UUID)
        state.zaaktype = zaaktype

        zaak = zrc_client.create('zaak', {
            'zaaktype': zaaktype['url'],
            'bronorganisatie': '517439943',
            'verantwoordelijkeOrganisatie': '223122166',
            'startdatum': '2018-06-01',
            'registratiedatum': '2018-06-18',
        })

        assert 'url' in zaak
        state.zaak = zaak

        # TODO check if the notif message was delivered to subscriber (drc) ???

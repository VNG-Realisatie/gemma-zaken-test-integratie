============
Installation
============

The project is developed in Python using the `Django framework`_. There are 3
sections below, focusing on developers, running the project using Docker and
hints for running the project in production.

.. _Django framework: https://www.djangoproject.com/


Development
===========


Prerequisites
-------------

You need have all the following components, and to satisfy their prerequisites :

* `Zaak Registratie Component`_ (ZRC)
* `Document Registratie Component`_ (DRC)
* `Overige Registratie Component`_ (ORC)
* `Zaak Type Catalogus`_ (ZTC)

.. _Zaak Registratie Component: https://github.com/maykinmedia/gemma-zaakregistratiecomponent
.. _Document Registratie Component: https://github.com/maykinmedia/gemma-documentregistratiecomponent
.. _Overige Registratie Component: https://github.com/maykinmedia/gemma-mock-overigeregistratiecomponenten
.. _Zaak Type Catalogus: https://github.com/maykinmedia/gemma-zaaktypecatalogus


You need the following libraries and/or programs:

* `Python`_ 3.4 or above
* Python `Virtualenv`_ and `Pip`_
* `PostgreSQL`_ 9.1 or above, with postgis extension
* `Node.js`_
* `npm`_

.. _Python: https://www.python.org/
.. _Virtualenv: https://virtualenv.pypa.io/en/stable/
.. _Pip: https://packaging.python.org/tutorials/installing-packages/#ensure-pip-setuptools-and-wheel-are-up-to-date
.. _PostgreSQL: https://www.postgresql.org
.. _Node.js: http://nodejs.org/
.. _npm: https://www.npmjs.com/


Getting started
---------------

Developers can follow the following steps to set up the project on their local
development machine.

Obtain source
^^^^^^^^^^^^^^

You can retrieve the source code using the following command:

   .. code-block:: bash

        $ git clone git@github.com:maykinmedia/gemma-zaken-test-integratie.git

**Note:** You can also use the HTTPS syntax:

   .. code-block:: bash

        $ git clone https://github.com/maykinmedia/gemma-zaken-test-integratie.git

Setting up virtualenv
^^^^^^^^^^^^^^^^^^^^^^

1. Go to the project directory:

   .. code-block:: bash

        $ cd gemma-zaken-test-integratie

2. Create the virtual environment:

   .. code-block:: bash

       $ virtualenv -p /usr/bin/python3.x ./env

3. Source the activate script in your virtual environment to enable it:

   .. code-block:: bash

       $ source env/bin/activate

4. Install all the required libraries:

   .. code-block:: bash

       (env) $ pip install -r requirements.txt


Writing a test
^^^^^^^^^^^^^^^^^

* You can instantiate clients thanks to the ``Client`` class, that use the file
  ``config.yml`` to get the configuration corresponding to the component.

* You can exchange data with the clients, following their schema. You can
  visualize the schema of each client at the corresponding url :
  ``http://localhost:<port_used>/api/v1/schema/``

Launching a test
-----------------

1. Follow the instructions in the appropriate ``INSTALL.rst`` files, to configure
and launch the 4 components (ZRC, DRC, ORC and ZTC).

Make sure you use the correct port for each test server, you can find the
configuration to use in the file ``config.yml``.
For example for ZRC, you need to use the following command :

   .. code-block:: bash

       (env) $ python src/manage.py runserver localhost:10000

2. Launch the test with pytest. For example if you want to launch
``test_userstory_39.py`` :

    .. code-block:: bash

        (env) $  pytest tests/test_userstory_39.py


Using test data
-----------------

For some tests, you might need to use some test data.
For ``test_userstory_39.py``, the following fixture has been used :

``datamodel.json``

    .. code-block:: json

        [
        {
        "model": "datamodel.catalogus",
        "pk": 1,
        "fields": {
            "domein": "DMN",
            "rsin": "123456789",
            "contactpersoon_beheer_naam": "John Doe",
            "contactpersoon_beheer_telefoonnummer": "",
            "contactpersoon_beheer_emailadres": ""
        }
        },
        {
        "model": "datamodel.roltype",
        "pk": 1,
        "fields": {
            "datum_begin_geldigheid": "2018-06-04",
            "datum_einde_geldigheid": null,
            "roltypeomschrijving": "APP melding overlast",
            "roltypeomschrijving_generiek": "Initiator",
            "soort_betrokkene": "[\"app\", \"api\"]",
            "is_van": 1
        }
        },
        {
        "model": "datamodel.statustype",
        "pk": 1,
        "fields": {
            "datum_begin_geldigheid": "2018-06-04",
            "datum_einde_geldigheid": null,
            "is_van": 1,
            "statustype_omschrijving": "Melding geregistreerd",
            "statustype_omschrijving_generiek": "",
            "statustypevolgnummer": 1,
            "doorlooptijd_status": null,
            "informeren": "J",
            "statustekst": "Nieuwe melding zwerfvuil",
            "toelichting": null,
            "checklistitem": [],
            "roltypen": [
                1
            ]
        }
        },
        {
        "model": "datamodel.productdienst",
        "pk": 1,
        "fields": {
            "naam": "Waterdienst",
            "link": null
        }
        },
        {
        "model": "datamodel.referentieproces",
        "pk": 1,
        "fields": {
            "naam": "zwerfvuil opruimen",
            "link": null
        }
        },
        {
        "model": "datamodel.zaaktype",
        "pk": 1,
        "fields": {
            "datum_begin_geldigheid": "2018-06-04",
            "datum_einde_geldigheid": null,
            "zaaktype_identificatie": 1,
            "zaaktype_omschrijving": "Zwerfvuil op het water",
            "zaaktype_omschrijving_generiek": "",
            "zaakcategorie": null,
            "doel": "Schoonhouden van de Amsterdamse grachten",
            "aanleiding": "Melding van zwerfvuil op het water",
            "toelichting": null,
            "indicatie_intern_of_extern": "Extern",
            "handeling_initiator": "melden",
            "onderwerp": "Melding",
            "handeling_behandelaar": "verwijderen",
            "doorlooptijd_behandeling": 1,
            "servicenorm_behandeling": null,
            "opschorting_aanhouding_mogelijk": "J",
            "verlenging_mogelijk": "J",
            "verlengingstermijn": 14,
            "trefwoord": "[]",
            "archiefclassificatiecode": null,
            "vertrouwelijkheidaanduiding": "OPENBAAR",
            "verantwoordelijke": "Waternet",
            "publicatie_indicatie": "N",
            "publicatietekst": null,
            "verantwoordingsrelatie": "[]",
            "versiedatum": "2018-06-04",
            "referentieproces": 1,
            "broncatalogus": null,
            "bronzaaktype": null,
            "maakt_deel_uit_van": 1,
            "product_dienst": [
                1
            ],
            "formulier": [],
            "is_deelzaaktype_van": []
        }
        }
        ]


This file has been loaded inside an empty database for ZTC, with the
following command :

    .. code-block:: bash

      (env) $  python manage.py loaddata path/to/datamodel.json

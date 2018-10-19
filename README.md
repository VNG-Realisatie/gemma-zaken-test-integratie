# GEMMA-ZAKEN integratietests

[![Build Status](https://jenkins.nlx.io/buildStatus/icon?job=gemma-zaken-test-integratie-master)](https://jenkins.nlx.io/view/Gemma/job/gemma-zaken-test-integratie-master/)

Dit project bevat integratietests voor de verschillende referentiecomponenten
betrokken in zaakgericht werken. In
[gemma-zaken](https://github.com/vng-Realisatie/gemma-zaken) wordt gewerkt aan
de ZDS 2.0 standaard, waar de API in componenten opgeknipt wordt. De
integratietests garanderen dat deze componenten ook effectief samen kunnen
werken.

## Voor wie is dit bedoeld?

In de eerste plaats worden deze tests gebruikt om de eigen referentie-implementaties
te testen:

* https://github.com/vng-Realisatie/gemma-zaakregistratiecomponent
* https://github.com/vng-Realisatie/gemma-documentregistratiecomponent
* https://github.com/vng-Realisatie/gemma-zaaktypecatalogus

Daarnaast kan een leverancier deze tests uitvoeren tegen hun eigen
implementaties van deze componenten, om de correctheid van de implementatie
te testen.

## Aan de slag

Clone deze repository, of download de code.

```bash
git clone https://github.com/vng-Realisatie/gemma-zaken-test-integratie.git
cd gemma-zaken-test-integratie
```

### Referentiecomponenten testen

De referentiecomponenten kunnen getest worden met `docker-compose`. Het volledige
script hiervoor is:

```bash
./jenkins.sh
```

### Eigen implementaties testen

#### Met docker

Ook voor het testen van eigen implementaties kan `docker-compose` gebruikt
worden.

Voorwaarde: de componenten die je wil testen zijn als Docker container beschikbaar

1. Bewerk `docker-compose.yml` zodat de `image` van de relevante componenten
   naar je eigen images wijst.
2. Voer `./jenkins.sh` uit

Eventueel kan je ook een extra override toevoegen waarbij de images aangepast
worden, en deze opnemen in de bron van `jenkins.sh`.

#### Zonder docker

Zonder docker oet je een Python-environment opstarten waarbinnen de tests
uitgevoerd worden. Python 3.6 is getest en officieel supported.

1. Maak een virtualenv aan en installeer de dependencies:

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```

2. Pas de `config.yml` aan zodat naar de juiste netwerklocatie van je
   componenten verwezen wordt.

3. Voer de tests uit:

```bash
pytest
```

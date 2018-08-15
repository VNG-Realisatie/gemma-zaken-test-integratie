# GEMMA-ZAKEN integratietests

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

Om de eigen implementaties te testen moet je een Python-environment opstarten.

Python 3.6 is getest.

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

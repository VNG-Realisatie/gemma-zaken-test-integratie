#!/bin/sh

# intended to be run from the root of the repo

set -e  # exit on error

echo "current directory: $(pwd)"

echo "Writing config file..."

cat >config.yml <<EOL
---

zrc:
  scheme: http
  host: zrc.vng
  port: 8000
  auth:
    client_id: zit
    secret: zrc-super-secret-key
    scopes: []

drc:
  scheme: http
  host: drc.vng
  port: 8000

ztc:
  scheme: http
  host: ztc.vng
  port: 8000
  auth:
    client_id: zit
    secret: ztc-super-secret-key
    scopes:
      - zds.scopes.zaaktypes.lezen

brc:
  scheme: http
  host: brc.vng
  port: 8000

orc:
  scheme: http
  host: orc.vng
  port: 8000

EOL

echo "Using config:"
cat config.yml

# run the test suite

pytest \
    --junitxml=reports/junit.xml \
    -s

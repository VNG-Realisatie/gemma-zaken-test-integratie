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

drc:
  scheme: http
  host: drc.vng
  port: 8000

ztc:
  scheme: http
  host: ztc.vng
  port: 8000

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

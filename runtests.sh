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
    client_id: demo
    secret: demo

drc:
  scheme: http
  host: drc.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo

ztc:
  scheme: http
  host: ztc.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo

brc:
  scheme: http
  host: brc.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo

orc:
  scheme: http
  host: orc.vng
  port: 8000

nc:
  scheme: http
  host: nc.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo

ac:
  scheme: http
  host: ac.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo
EOL

echo "Using config:"
cat config.yml

# run the test suite

pytest \
    --junitxml=reports/junit.xml \
    -s

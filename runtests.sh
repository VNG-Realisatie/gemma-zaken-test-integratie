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
    user_id: docker
    user_representation: docker

drc:
  scheme: http
  host: drc.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo
    user_id: docker
    user_representation: docker

ztc:
  scheme: http
  host: ztc.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo
    user_id: docker
    user_representation: docker

brc:
  scheme: http
  host: brc.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo
    user_id: docker
    user_representation: docker

orc:
  scheme: http
  host: orc.vng
  port: 8000

nrc:
  scheme: http
  host: nrc.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo
    user_id: docker
    user_representation: docker

ac:
  scheme: http
  host: ac.vng
  port: 8000
  auth:
    client_id: demo
    secret: demo
    user_id: docker
    user_representation: docker
EOL

echo "Using config:"
cat config.yml

# run the test suite

pytest \
    --junitxml=reports/junit.xml \
    -s

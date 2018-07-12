#!/bin/sh

# intended to be run from the root of the repo

set -e  # exit on error

echo "current directory: $(pwd)"

echo "Writing config file..."

cat >config.yml <<EOL
---

zrc:
  scheme: http
  host: zrc_web
  port: 8000

drc:
  scheme: http
  host: drc_web
  port: 8000

ztc:
  scheme: http
  host: ztc_web
  port: 8000

orc:
  scheme: http
  host: orc_web
  port: 8000

EOL

echo "Using config:"
cat config.yml

pytest

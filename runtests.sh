#!/bin/sh

# intended to be run from the root of the repo

set -e  # exit on error

# TODO: wait until all services are up

until curl -sSf http://zrc.vng:8000/ > /dev/null; do
    >&2 echo "Waiting until ZRC is up..."
    sleep 1
done

until curl -sSf http://drc.vng:8000/ > /dev/null; do
    >&2 echo "Waiting until DRC is up..."
    sleep 1
done

until curl -sSf http://ztc.vng:8000/ > /dev/null; do
    >&2 echo "Waiting until ZTC is up..."
    sleep 1
done

until curl -sSf http://orc.vng:8000/ > /dev/null; do
    >&2 echo "Waiting until ORC is up..."
    sleep 1
done

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

orc:
  scheme: http
  host: orc.vng
  port: 8000

EOL

echo "Using config:"
cat config.yml

pytest

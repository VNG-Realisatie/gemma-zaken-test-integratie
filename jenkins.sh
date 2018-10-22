#!/bin/bash

set -e  # exit on errors
set -x  # echo commands

if [[ -z "$WORKSPACE" ]]; then
    export WORKSPACE=$(pwd)
fi

# fetch latest images
docker-compose pull

# bring up the services
docker-compose up --detach

# build tests image
docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    build tests

# wait until all services are up

# TODO: port binding/exposing should not happen here to not affect other
# builds using the same ports

until curl -sSf http://localhost:8000/ > /dev/null; do
    >&2 echo "Waiting until ZRC is up..."
    sleep 1
done

until curl -sSf http://localhost:8001/ > /dev/null; do
    >&2 echo "Waiting until DRC is up..."
    sleep 1
done

until curl -sSf http://localhost:8002/ > /dev/null; do
    >&2 echo "Waiting until ZTC is up..."
    sleep 1
done

until curl -sSf http://localhost:8003/ > /dev/null; do
    >&2 echo "Waiting until BRC is up..."
    sleep 1
done

until curl -sSf http://localhost:8010/ > /dev/null; do
    >&2 echo "Waiting until ORC is up..."
    sleep 1
done

# FIXME: services need to be running first
# docker-compose \
#     -f ./docker-compose.yml \
#     -f docker-compose.jenkins.yml \
#     exec -u postgres zrc_db \
#         update-postgis.sh

# prepare DRC
docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    run drc.vng \
        python src/manage.py loaddata fixtures/drc.json

# prepare ZTC
docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    run ztc.vng \
        python src/manage.py loaddata fixtures/ztc.json

# even on errors, continue because we need to bring down the containers
set +e

# run tests
docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    run tests

failure=$?

set -e

# shut everything down if debug not enabled
if [ -z "$DEBUG" ]; then
    docker-compose \
        -f ./docker-compose.yml \
        -f docker-compose.jenkins.yml \
        down \
        --volumes
else
    echo "Not bringing services down, debug is enabled"
fi

exit $failure

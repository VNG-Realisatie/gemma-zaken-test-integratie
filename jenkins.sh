#!/bin/bash

set -e  # exit on errors
set -x  # echo commands

if [[ -z "$WORKSPACE" ]]; then
    export WORKSPACE=$(pwd)
fi

docker-compose pull

# build tests image
docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    build tests

# prepare DRC
docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    run drc.vng \
        python src/manage.py migrate

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
        python src/manage.py migrate

docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    run ztc.vng \
        python src/manage.py loaddata fixtures/ztc.json

set +e  # even on errors, continue because we need to bring down the containers

# run tests
docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    run tests

failure=$?

# shut everything down
docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    down

exit $failure

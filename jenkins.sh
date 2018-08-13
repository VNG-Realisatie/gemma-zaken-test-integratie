#!/bin/bash

set -e  # exit on errors
set -x  # echo commands

if [[ -z "$WORKSPACE" ]]; then
    export WORKSPACE=$(pwd)
fi

docker-compose pull

docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    build tests

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

docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    run tests

docker-compose \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    down

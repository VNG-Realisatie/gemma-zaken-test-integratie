#!/bin/bash

set -e  # exit on errors
set -x  # echo commands

if [[ -z "$WORKSPACE" ]]; then
    export WORKSPACE=$(pwd)
fi

docker-compose \
    -p zit \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    build tests

docker-compose \
    -p zit \
    -f ./docker-compose.yml \
    -f docker-compose.jenkins.yml \
    run ztc_web \
    python src/manage.py loaddata fixtures/ztc.json

# docker-compose -p zit -f ./docker-compose.yml run tests

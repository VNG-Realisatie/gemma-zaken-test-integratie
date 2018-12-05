# Stage 1 - Python build environment
FROM python:3.6-alpine as build

RUN apk --no-cache add \
    build-base \
    python-dev \
    # pillow dependencies
    jpeg-dev \
    openjpeg-dev \
    zlib-dev

WORKDIR /testenv

COPY requirements.txt .
RUN pip install -r requirements.txt


# Stage 2 - Python test environment
FROM python:3.6-alpine

RUN apk --no-cache add \
    curl \
    # pillow dependencies
    jpeg \
    openjpeg \
    zlib

COPY --from=build /usr/local/lib/python3.6 /usr/local/lib/python3.6
COPY --from=build /usr/local/bin/pytest /usr/local/bin/pytest
COPY --from=build /usr/local/bin/py.test /usr/local/bin/py.test

WORKDIR /testenv

COPY setup.cfg .
COPY runtests.sh .

# copy test code
COPY tests ./tests/

CMD ["/testenv/runtests.sh"]

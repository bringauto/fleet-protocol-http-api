#!/bin/bash

#coverage run --omit="**/__init__.py, /usr/**" --branch -m unittest discover -s src/tests;

pushd server
coverage run --omit="**/__init__.py" --branch -m unittest discover -s fleetv2_http_api/impl/tests
coverage report -m
coverage run --omit="**/__init__.py" --branch -m unittest discover -s database/impl/tests
coverage report -m
popd
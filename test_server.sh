#!/bin/bash

omit_files="**/__init__.py,./fleetv2_http_api/models/*,fleetv2_http_api/util.py,fleetv2_http_api/typing_utils.py"

pushd server
coverage run --omit=$omit_files  --branch -m unittest discover -s fleetv2_http_api/impl/tests
coverage report -m
coverage run --omit=$omit_files --branch -m unittest discover -s database/tests
coverage report -m
popd
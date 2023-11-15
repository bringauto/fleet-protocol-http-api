#!/bin/bash


pushd server
python3 -m unittest discover -s fleetv2_http_api/impl/tests
popd
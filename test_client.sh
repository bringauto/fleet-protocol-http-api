#!/bin/bash


pushd client
python3 -m unittest discover -s http_api_client/impl
popd
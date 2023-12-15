#!/bin/bash

pushd server
npx @openapitools/openapi-generator-cli generate -i ../openapi.yaml -g python-flask -o . --additional-properties=packageName=fleetv2_http_api
popd
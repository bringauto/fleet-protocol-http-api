#! /bin/bash


kill $(fuser 8080/tcp)

pushd server
npx @openapitools/openapi-generator-cli generate -g python-flask -i ../openapi.yaml -o . -p=packageName=fleetv2_http_api
popd

pushd client
npx @openapitools/openapi-generator-cli generate -g python -i ../openapi.yaml -o . -p=packageName=http_api_client
popd


python3 -m server &

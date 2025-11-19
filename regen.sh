#!/bin/bash

pushd server
npx @openapitools/openapi-generator-cli generate -i ../openapi.yaml -g python-flask -o . --additional-properties=packageName=fleetv2_http_api
popd

# Fix imports
find server/fleetv2_http_api -type f \( -name "*.py" -o -name "*.yaml" \) -exec sed -i 's/ fleetv2_http_api/ server.fleetv2_http_api/g' {} +
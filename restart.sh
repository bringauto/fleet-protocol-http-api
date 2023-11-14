#! /bin/bash


kill $(fuser 8080/tcp)

pushd server
python3 -m fleetv2_http_api &
popd

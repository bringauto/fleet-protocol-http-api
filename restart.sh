#! /bin/bash


kill $(fuser 8080/tcp)

python3 -m fleetv2_http_api &


#! /bin/bash


kill $(fuser 8080/tcp)
python3 -m server &

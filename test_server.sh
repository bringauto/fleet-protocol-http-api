#!/bin/bash

omitted_files="*/__init__.py,*/models/*,*/typing_utils.py,*/util.py,enums.py"

pushd server
coverage run --omit=$omitted_files -m unittest discover -s database/tests -p "test_*.py" 
coverage run --omit=$omitted_files -a -m unittest discover -s fleetv2_http_api/impl/tests -p "test_*.py" 
coverage report --data-file=.coverage
popd
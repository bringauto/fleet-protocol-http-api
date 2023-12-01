# Fleet v2 Python server

## Overview
This server was generated by the [OpenAPI Generator](https://openapi-generator.tech) project. By using the
[OpenAPI-Spec](https://openapis.org) from a remote server, you can easily generate a server stub.  This
is an example of building a OpenAPI-enabled Flask server.

This example uses the [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requirements
Python 3.5.2+

## Usage
To run the server, please execute the following from the root directory:

```bash
pip3 install -r requirements.txt
python3 -m server
```

and open your browser to here:

```
http://localhost:8080/ui/
```

Your OpenAPI definition lives here:

```
http://localhost:8080/openapi.json


```
## Running with Docker

To run the server on a Docker container (together with the PostgreSQL database), please execute the following from the root directory:

```bash
# build all and start in detached mode
docker compose up --build -d
```

## Adding new admin to the database

To add generate new api_key (passed as a query parameter "api_key") run the following:
```bash 
python scripts/new_admin.py -usr '<db-username>' -pwd '<db-password>' '<new-admin-name>' 
```

Working example for test database build from docker compose (username and password can be found in the config.json):
```bash 
python scripts/new_admin.py -usr 'postgres' -pwd '1234' 'Řehoř' 
```
After running the script, the api_key is printed to console: 
```bash

New key for admin 'Řehoř':

MzLwgWGitBSDTNLjqktSnzNZQAjKaC

```


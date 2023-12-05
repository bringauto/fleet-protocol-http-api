# Fleet v2 server


The HTTP API is described by the `openapi.yaml` according to [OpenAPI Specification](https://openapis.org).

The base of the server (e.g., entity models) was generated by the [OpenAPI Generator](https://openapi-generator.tech) project. This includes ALL the contents of the `server/fleetv2_http_api` directory EXCEPT for:
- `impl`,
- `controllers/security_controller.py` (originally created by the Generator).

These files are included in the `server/.openapi-generator-ignore`. This file also must include itself.


## Requirements
Python 3.5.2+

## Server re-generation
You must have the OpenAPI Generator installed (see [link](https://openapi-generator.tech/docs/installation/)). Before the server generation, the server must be STOPPED.

To regenerate the server run (in the `server` directory):
```bash
openapi-generator-cli generate -g python-flask -i ../openapi.yaml -o . -p=packageName=fleetv2_http_api
```
Below is an example of running generator with the port number being specified (the default is `8080`):
```bash
openapi-generator-cli generate -g python-flask -i ../openapi.yaml -o . -p=packageName=fleetv2_http_api,serverPort=<port-number>
```
If you have trouble with running the generator, visit [docs](https://openapi-generator.tech/docs/installation/).


## Usage
To run the server execute the following from the root directory:

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
### Running with Docker

To run the server on a Docker container, run:

```bash
docker compose up --build -d
```

### Adding a new admin to the database

To generate a new api_key (passed as a query parameter "api_key") run the following:
```bash 
python scripts/new_admin.py -usr '<db-username>' -pwd '<db-password>' '<new-admin-name>' 
```

Working example for test database built from docker-compose (username and password can be found in the `config.json`).
```bash 
python scripts/new_admin.py -usr 'postgres' -pwd '1234' 'Bob' 
```
After running the script, the api_key is printed to the console: 
```bash
New key for admin 'Bob':

MzLwgWGitBSDTNLjqktSnzNZQAjKaC
```

### Configuration
The server settings can be found in the `config.json`, including the database logging information and parameters for the database cleanup.





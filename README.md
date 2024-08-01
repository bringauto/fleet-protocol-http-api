# Fleet v2 server

The HTTP API is described by the `openapi.yaml` according to [OpenAPI Specification](https://openapis.org).

The base of the server (e.g., entity models) was generated by the [OpenAPI Generator](https://openapi-generator.tech) project. This includes ALL the contents of the `server/fleetv2_http_api` directory EXCEPT for:

- `impl`,
- `controllers/security_controller.py` (originally created by the Generator).

These files are included in the `server/.openapi-generator-ignore`. This file also must include itself.

## Requirements

Python 3.10.12+

## Server re-generation

You must have the OpenAPI Generator installed (see [link](https://openapi-generator.tech/docs/installation/)). Before the server generation, the server must be STOPPED.

To regenerate the server, run (in the `server` directory):

```bash
openapi-generator-cli generate -g python-flask -i ../openapi.yaml -o . -p=packageName=fleetv2_http_api
```

Below is an example of running the Generator with the port number being specified (the default is `8080`):

```bash
openapi-generator-cli generate -g python-flask -i ../openapi.yaml -o . -p=packageName=fleetv2_http_api,serverPort=<port-number>
```

If you have trouble with running the generator, visit [docs](https://openapi-generator.tech/docs/installation/).

## Tests

Testing of a cloned repository requires two steps:

- install this package,
- run the tests (or their subset).

**Before installation, make sure you have the [virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments) activated.** This is a necessary step to avoid conflicts with the system packages.

## Package installation

Run the command below in the root directory. `-e` is used to install the package in the [editable mode](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#working-in-development-mode).

```bash
pip install [-e] .
```

## Running the tests

In the root directory, run the following

```bash
python -m tests [-h] [PATH1] [PATH2] ...
```

Each PATH is specified relative to the `tests` directory. If no PATH is specified, all the tests will run. Otherwise

- when PATH is a directory, the script will run all tests in this directory (and subdirectories),
- when PATH is a Python file, the script will run all tests in the file.

The `-h` flag makes the script display tests' coverage in an HTML format, for example in your web browser.

The same applies to integration tests using containerized HTTP servers.

To run the integration tests, run the following in the root directory:

```bash
python -m tests_integration [-h] [PATH1] [PATH2] ...
```

## Usage

To run the server execute the following from the root directory:

```bash
pip3 install -r requirements.txt
python3 -m server <path-to-config-file> [OPTIONS]
```

The server automatically connects to the PostgreSQL database using data from the config file. If you want to override these values, start the server with some of the following options:

| Option            | Short  | Description                                  |
| ----------------- | ------ | -------------------------------------------- |
| `--username`      | `-usr` | Username for the PostgreSQL database         |
| `--password`      | `-pwd` | Password for the PostgreSQL database         |
| `--location`      | `-l`   | Location of the database (e.g., `localhost`) |
| `--port`          | `-p`   | Port number (e.g., `5430`)                   |
| `--database-name` | `-db`  | Database name                                |

Note that these data should comply with the requirements specified in SQLAlchemy [documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls).

To visualize the API, open your browser here (the location and port may vary according to the script parameters or the values in `config/config.json`):

```
http://localhost:8080/v2/protocol/ui
```

Your OpenAPI definition lives here:

```
http://localhost:8080/v2/protocol/openapi.json
```

### Running with Docker

To run the server on a Docker container, run:

```bash
docker compose up --build -d
```

### Adding a new admin to the database

To generate a new api_key (passed as a query parameter "api_key") run the following:

```bash
python scripts/new_admin.py <new-admin-name> <path-to-config-file> [OPTIONS]
```

The script automatically connects to the PostgreSQL database using the config file. To override any of those values, run the script with some of the following options:

| Option            | Short  | Description                                  |
| ----------------- | ------ | -------------------------------------------- |
| `--username`      | `-usr` | Username for the PostgreSQL database         |
| `--password`      | `-pwd` | Password for the PostgreSQL database         |
| `--location`      | `-l`   | Location of the database (e.g., `localhost`) |
| `--port`          | `-p`   | Port number (e.g., `5430`)                   |
| `--database-name` | `-db`  | Database name                                |

Note that these data should comply with the requirements specified in SQLAlchemy [documentation](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls).

Working example for test database built from docker-compose (username and password can be found in the `config/config.json`).

```bash
python scripts/new_admin.py 'Bob' config/config.json
```

After running the script, the api_key is printed to the console:

```bash
New key for admin 'Bob':

MzLwgWGitBSDTNLjqktSnzNZQAjKaC
```

### Configuring oAuth2

To get Keycloak authentication working, all parameters in the security section of `config/config.json` need to be filled in. Most information is found in the Keycloak GUI.

```json
"security": {
        "keycloak_url": "https://keycloak.bringauto.com",
        "client_id": "",
        "client_secret_key": "",
        "scope": "",
        "realm": ""
    }
```

- keycloak_url: base URL of a working Keycloak instance
- client_id: id of client in Keycloak (Clients -> click on client representing HTTP API -> Settings -> Client ID)
- client_secret_key: secret key of client (Clients -> click on client representing HTTP API -> Credentials -> Client Secret)
- scope: checking of scopes is not yet implemented (must be `email` for now!)
- realm: realm in which the client belongs (seen on top of the left side panel in Keycloak GUI)

### Configuration

The server settings can be found in the `config/config.json`, including the database logging information and parameters for the database cleanup.

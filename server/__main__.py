import logging

import requests  # type: ignore
import connexion  # type: ignore
from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from sqlalchemy.orm import Session
from importlib.resources import files as importlib_files
from yaml import safe_load as load_yaml  # type: ignore

from server.fleetv2_http_api import encoder  # type: ignore
from server.config import CleanupTiming, DBFile
from server.database.database_controller import remove_old_messages, set_message_retention_period  # type: ignore
from server.database.cache import clear_connected_cars  # type: ignore
from server.database.connection import set_db_connection, set_test_db_connection, get_test_db_connection  # type: ignore
from server.database.time import timestamp  # type: ignore
from server.database.security import _AdminBase

# The import here should be left as it is without the server. part. It must match the paths in the openapi.yaml file
# to prevent duplicit imports.
import server.fleetv2_http_api.impl.controllers as api_controllers  # type: ignore
from server.fleetv2_http_api.controllers.security_controller import set_auth_params  # type: ignore
import server.database.script_args as script_args  # type: ignore
from server.logs import configure_logging, LOGGER_NAME
import server.fleetv2_http_api as server_package


COMPONENT_NAME = "Fleet Protocol HTTP API"
APP_NAME = "Fleet v2 HTTP API"


logger = logging.getLogger(LOGGER_NAME)


def _clean_up_messages() -> None:
    """Clean up messages from the database."""
    remove_old_messages(current_timestamp=timestamp())


def _connect_to_database(vals: script_args.ScriptArgs) -> None:
    """Clear previously stored available devices and connect to the database."""
    clear_connected_cars()

    if isinstance(vals.config.database.server, DBFile):
        set_test_db_connection(db_name=vals.config.database.server.path)
        source = get_test_db_connection(db_name=vals.config.database.server.path)
        if source is None:
            raise RuntimeError("Failed to create database connection.")
        with Session(source) as session:
            admin = _AdminBase(name="default_key", key="DefaultKey")
            session.add(admin)
            session.commit()
    else:
        set_db_connection(
            dblocation=vals.argvals["location"],
            port=vals.argvals["port"],
            username=vals.argvals["username"],
            password=vals.argvals["password"],
            db_name=vals.argvals["database_name"],
        )


def _set_up_database_jobs(config: CleanupTiming) -> None:
    """Set message cleanup job and other customary jobs defined by the example method."""
    set_message_retention_period(config.retention_period)
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=_clean_up_messages,
        trigger="interval",
        seconds=config.cleanup_period,
    )
    scheduler.start()


def _retrieve_keycloak_public_key(keycloak_url: str, realm: str) -> str:
    """Retrieve the public key from the Keycloak server."""
    try:
        response = requests.get(keycloak_url.rstrip("/") + "/realms/" + realm)
        response.raise_for_status()
        logger.info("Retrieved public key from Keycloak server.")
        return response.json()["public_key"]
    except Exception as e:
        logger.warning("Failed to retrieve public key from Keycloak server. Error: %s", e)
        return ""


def run_server(port: int = 8080) -> None:
    """Run the Fleet Protocol v2 HTTP API server."""
    app = connexion.App(APP_NAME.lower().replace(" ", "-"))
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        load_yaml(importlib_files(server_package).joinpath("openapi/openapi.yaml").read_text()),
        arguments={"title": "Fleet Protocol v2 HTTP API"},
        pythonic_params=True,
    )
    app.run(port=port)


def main() -> None:
    vals = script_args.request_and_get_script_arguments(
        "Run the Fleet Protocol v2 HTTP API server."
    )
    config = vals.config
    configure_logging(COMPONENT_NAME, config)
    _connect_to_database(vals)
    _set_up_database_jobs(config.database.cleanup.timing_in_seconds)
    api_controllers.set_car_wait_timeout_s(config.request_for_messages.timeout_in_seconds)
    api_controllers.set_status_wait_timeout_s(config.request_for_messages.timeout_in_seconds)
    api_controllers.set_command_wait_timeout_s(config.request_for_messages.timeout_in_seconds)
    api_controllers.init_oauth(config.security, str(config.http_server.base_uri))
    set_auth_params(
        public_key=_retrieve_keycloak_public_key(
            keycloak_url=str(config.security.keycloak_url), realm=config.security.realm
        ),
        client_id=config.security.client_id,
    )
    run_server(config.http_server.port)


if __name__ == "__main__":
    main()

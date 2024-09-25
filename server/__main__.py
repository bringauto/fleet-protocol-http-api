import sys
sys.path.append("server")
import logging
import requests  # type: ignore

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore

from server.database.database_controller import remove_old_messages, set_message_retention_period  # type: ignore
from server.database.cache import clear_connected_cars  # type: ignore
from server.database.connection import set_db_connection  # type: ignore
from server.database.time import timestamp  # type: ignore
from server.fleetv2_http_api.__main__ import main as run_server  # type: ignore
from server.fleetv2_http_api.impl.controllers import (  # type: ignore
    set_car_wait_timeout_s,
    set_status_wait_timeout_s,
    set_command_wait_timeout_s,
    init_security
)
from server.fleetv2_http_api.controllers.security_controller import set_auth_params  # type: ignore
import server.database.script_args as script_args  # type: ignore
from server.logs import configure_logging, LOGGING_CONFIG_PATH, LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


def _clean_up_messages() -> None:
    """Clean up messages from the database."""
    remove_old_messages(current_timestamp=timestamp())


def _connect_to_database(vals:script_args.ScriptArgs) -> None:
    """Clear previously stored available devices and connect to the database."""
    clear_connected_cars()
    set_db_connection(
        dblocation = vals.argvals["location"],
        port = vals.argvals["port"],
        username = vals.argvals["username"],
        password = vals.argvals["password"],
        db_name = vals.argvals["database_name"]
    )


def _set_up_database_jobs(db_cleanup_config: dict[str,int]) -> None:
    """Set message cleanup job and other customary jobs defined by the example method."""
    set_message_retention_period(db_cleanup_config["retention_period"])
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=_clean_up_messages,
        trigger="interval",
        seconds=db_cleanup_config["cleanup_period"],
    )
    scheduler.start()


def _retrieve_keycloak_public_key(keycloak_url: str, realm: str) -> str:
    """Retrieve the public key from the Keycloak server."""
    try:
        response = requests.get(keycloak_url + "/realms/" + realm)
        response.raise_for_status()
    except:
        logger.warning("Failed to retrieve public key from Keycloak server.")
        return ""
    logger.info("Retrieved public key from Keycloak server.")
    return response.json()["public_key"]


COMPONENT_NAME = "Fleet Protocol HTTP API"


if __name__ == '__main__':
    vals = script_args.request_and_get_script_arguments("Run the Fleet Protocol v2 HTTP API server.")
    config = vals.config
    configure_logging("Fleet Protocol HTTP API", config)
    _connect_to_database(vals)
    _set_up_database_jobs(config["database"]["cleanup"]["timing_in_seconds"])
    set_car_wait_timeout_s(config["request_for_messages"]["timeout_in_seconds"])
    set_status_wait_timeout_s(config["request_for_messages"]["timeout_in_seconds"])
    set_command_wait_timeout_s(config["request_for_messages"]["timeout_in_seconds"])
    init_security(
        keycloak_url=config["security"]["keycloak_url"],
        client_id=config["security"]["client_id"],
        secret_key=config["security"]["client_secret_key"],
        scope=config["security"]["scope"],
        realm=config["security"]["realm"],
        callback=config["http_server"]["base_uri"]
    )
    set_auth_params(
        public_key=_retrieve_keycloak_public_key(
            keycloak_url=config["security"]["keycloak_url"],
            realm=config["security"]["realm"]
        ),
        client_id=config["security"]["client_id"]
    )
    run_server()

import sys
sys.path.append("server")
from typing import Dict
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from database.database_controller import remove_old_messages, set_message_retention_period
from database.device_ids import clear_device_ids
from database.connection import set_db_connection
from database.time import timestamp
from fleetv2_http_api.__main__ import main as run_server
from fleetv2_http_api.impl.controllers import set_status_wait_timeout_s, set_command_wait_timeout_s, init_security
from fleetv2_http_api.controllers.security_controller import set_public_key
import database.script_args as script_args

def _clean_up_messages() -> None:
    """Clean up messages from the database."""
    remove_old_messages(current_timestamp=timestamp())

def _connect_to_database(vals:script_args.ScriptArgs) -> None:
    """Clear previously stored available devices and connect to the database."""
    clear_device_ids()
    set_db_connection(
        dblocation = vals.argvals["location"] + ":" + str(vals.argvals["port"]),
        username = vals.argvals["username"],
        password = vals.argvals["password"],
        db_name = vals.argvals["database_name"]
    )

def _set_up_database_jobs(db_cleanup_config: Dict[str,int]) -> None:
    """Set message cleanup job and other customary jobs defined by the example method."""
    set_message_retention_period(db_cleanup_config["retention_period"])
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=_clean_up_messages,
        trigger="interval",
        seconds=db_cleanup_config["cleanup_period"],
    )
    scheduler.start()


def _set_up_log_format() -> None:
    """Set up the logging format."""
    FORMAT = '%(asctime)s -- %(message)s'
    logging.basicConfig(format=FORMAT)


if __name__ == '__main__':
    vals = script_args.request_and_get_script_arguments("Run the Fleet Protocol v2 HTTP API server.")
    config = vals.config
    _set_up_log_format()
    _connect_to_database(vals)
    _set_up_database_jobs(config["database"]["cleanup"]["timing_in_seconds"])
    set_status_wait_timeout_s(config["request_for_messages"]["timeout_in_seconds"])
    set_command_wait_timeout_s(config["request_for_messages"]["timeout_in_seconds"])
    init_security(
        config["security"]["keycloak_url"],
        config["security"]["client_id"],
        config["security"]["client_secret_key"],
        config["security"]["scope"],
        config["security"]["realm"],
        config["http_server"]["base_uri"]
    )
    public_key_file = open(config["security"]["keycloak_public_key_file"], "r")
    set_public_key(public_key_file.read())
    public_key_file.close()
    run_server()

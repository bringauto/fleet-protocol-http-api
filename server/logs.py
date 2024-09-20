from __future__ import annotations
import json
import os
import logging.config

from typing import TypeVar, Mapping


T = TypeVar("T", bound=Mapping)


LOGGER_NAME = "werkzeug"
LOG_FILE_NAME = "fleet_protocol_http_api.log"
DEFAULT_LOG_DIR = "log"
DEFAULT_LOG_FORMAT = (
    "[%(asctime)s.%(msecs)03d] [fleet-protocol-http-api] [%(levelname)s]\t %(message)s"
)
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(log_config_path: str, component_name: str) -> None:
    """Configure the logging for the application.

    The component name is written in the log messages to identify the source of the log message.

    The logging configuration is read from a JSON file. If the file is not found, a default configuration is used.
    """
    try:
        with open(log_config_path) as f:
            logging.config.dictConfig(json.load(f))
    except Exception as e:
        logger = logging.getLogger(LOGGER_NAME)
        logger.warning(
            f"{component_name}: Could not find a logging configuration file (entered path: {log_config_path}. "
            f"Using default logging configuration. The error was: {e}"
        )
        default_log_path = os.path.join(DEFAULT_LOG_DIR, LOG_FILE_NAME)
        if not os.path.isfile(default_log_path):
            if not os.path.exists(DEFAULT_LOG_DIR):
                os.makedirs(DEFAULT_LOG_DIR)
            with open(default_log_path, "w") as f:
                f.write("")

        logger.propagate = False
        formatter = logging.Formatter(_default_log_format(component_name), DEFAULT_DATE_FORMAT)
        file_handler = logging.FileHandler(filename=default_log_path)
        file_handler.setLevel(level=logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level=logging.INFO)
        logger.addHandler(stream_handler)

        logger.setLevel(level=logging.INFO)


def _default_log_format(component_name: str) -> str:
    log_component_name = "-".join(component_name.lower().split())
    return f"[%(asctime)s.%(msecs)03d] [{log_component_name}] [%(levelname)s]\t %(message)s"



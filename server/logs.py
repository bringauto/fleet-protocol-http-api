from __future__ import annotations
import json
import os
import logging.config

from typing import TypeVar, Mapping


T = TypeVar("T", bound=Mapping)


DEFAULT_LOG_DIR = "log"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGING_CONFIG_PATH = "config/logging.json"


LOGGER_NAME = "werkzeug"


def configure_logging(component_name: str, logger_name: str) -> None:
    """Configure the logging for the application.

    The component name is written in the log messages to identify the source of the log message.

    The logging configuration is read from a JSON file. If the file is not found, a default configuration is used.
    """
    try:
        with open(LOGGING_CONFIG_PATH) as f:
            logging.config.dictConfig(json.load(f))
    except Exception as e:
        logger = logging.getLogger(logger_name)
        logger.warning(
            f"{component_name}: Could not find a logging configuration file (path to logging config: {os.path.abspath(LOGGING_CONFIG_PATH)}). "
            f"Using default logging configuration. The error was: {e}"
        )
        default_log_path = os.path.join(DEFAULT_LOG_DIR, _log_file_name(component_name))
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


def _log_file_name(component_name: str) -> str:
    return "_".join(component_name.lower().split())
from __future__ import annotations
import json
import os
import logging.config

from typing import TypeVar, Mapping


T = TypeVar("T", bound=Mapping)


LOG_FILE_NAME = "fleet_protocol_http_api.log"
LOGGER_NAME = "werkzeug"
LOGGING_CONFIG_PATH = "config/logging.json"
DEFAULT_LOG_DIR = "log"


def clear_logs() -> None:
    """Clear the log file."""
    log_file_path = _get_log_dir_path()
    with open(log_file_path, "w") as f:
        f.write("")


def _get_log_dir_path() -> str:
    try:
        with open(LOGGING_CONFIG_PATH) as f:
            config = json.load(f)
            return config["handlers"]["file"]["filename"]
    except:
        return DEFAULT_LOG_DIR


def configure_logging(config_path: str) -> None:
    try:
        with open(config_path) as f:
            logging.config.dictConfig(json.load(f))
    except Exception:
        logger = logging.getLogger(LOGGER_NAME)
        logger.warning(
            f"Fleet Protocol HTTP API: Could not find a logging configuration file (entered path: {config_path}. Using default logging configuration."
        )
        default_log_path = os.path.join(DEFAULT_LOG_DIR, LOG_FILE_NAME)
        if not os.path.isfile(default_log_path):
            if not os.path.exists(DEFAULT_LOG_DIR):
                os.makedirs(DEFAULT_LOG_DIR)
            with open(default_log_path, "w") as f:
                f.write("")

        logger.propagate = False
        formatter = logging.Formatter(
            fmt="[%(asctime)s.%(msecs)03d] [fleet-protocol-http-api] [%(levelname)s]\t %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(filename=default_log_path)
        file_handler.setLevel(level=logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level=logging.INFO)
        logger.addHandler(stream_handler)

        logger.setLevel(level=logging.INFO)

from __future__ import annotations
import json
import os
import logging.config

from typing import TypeVar, Mapping


T = TypeVar("T", bound=Mapping)


LOG_FILE_NAME = "fleet_protocol_http_api.log"


def clear_logs() -> None:
    """Clear the log file."""
    with open(f"log/{LOG_FILE_NAME}", "w") as f:
        f.write("")


def configure_logging(config_path: str) -> None:
    try:
        with open(config_path) as f:
            logging.config.dictConfig(json.load(f))
    except Exception:
        logger = logging.getLogger("werkzeug")
        logger.warning(
            f"Fleet Protocol HTTP API: Could not find a logging configuration file (entered path: {config_path}. Using default logging configuration."
        )
        if not os.path.isfile(f"log/{LOG_FILE_NAME}"):
            if not os.path.exists("log"):
                os.makedirs("log")
            with open(f"log/{LOG_FILE_NAME}", "w") as f:
                f.write("")

        logger.propagate = False
        formatter = logging.Formatter(
            fmt="[%(asctime)s.%(msecs)03d] [fleet-protocol-http-api] [%(levelname)s]\t %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(f"log/{LOG_FILE_NAME}")
        file_handler.setLevel(level=logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level=logging.INFO)
        logger.addHandler(stream_handler)

        logger.setLevel(level=logging.INFO)
        if not os.path.exists("log"):
            os.makedirs("log")

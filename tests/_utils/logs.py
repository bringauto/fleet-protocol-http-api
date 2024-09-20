import json
import logging

from server.logs import LOGGER_NAME, DEFAULT_LOG_DIR, LOGGING_CONFIG_PATH


def clear_logs() -> None:
    """Find and clear the log file."""
    log_file_path = _get_log_dir_path()
    with open(log_file_path, "w") as f:
        f.write("")


def _get_log_dir_path() -> str:
    try:
        with open(LOGGING_CONFIG_PATH) as f:
            log_config = json.load(f)
            return log_config["handlers"]["file"]["filename"]
    except Exception as e:
        logger = logging.getLogger(LOGGER_NAME)
        logger.warning(
            f"Error when attepting to find a configuration file. Using default logging configuration. The error was: {e}"
        )
        return DEFAULT_LOG_DIR



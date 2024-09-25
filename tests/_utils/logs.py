import json
import os


def clear_logs() -> None:
    """Find and clear the log file."""
    dir = os.path.dirname(__file__)
    config = json.loads(open(os.path.join(dir,"test_config.json")).read())
    log_file_path = config["general-settings"]["log-path"]
    with open(log_file_path, "w") as f:
        f.write("")

<<<<<<< HEAD

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


=======
>>>>>>> @{-1}

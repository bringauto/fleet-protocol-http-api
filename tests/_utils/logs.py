import json
import os


def clear_logs() -> None:
    """Find and clear the log file."""
    dir = os.path.dirname(__file__)
    with open(os.path.join(dir, "test_config.json"), "r") as f:
        config = json.load(f)
    log_file_path = config["general-settings"]["log-path"]
    with open(log_file_path, "w") as f:
        f.write("")


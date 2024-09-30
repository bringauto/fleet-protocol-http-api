import json
import os


def clear_logs() -> None:
    """Find and clear the log file."""
    directory = os.path.dirname(__file__)
    with open(os.path.join(directory, "test_config.json"), "r") as f:
        config = json.load(f)
    log_file_path = config["logging"]["log-path"]
    if not os.path.exists(log_file_path):
        return
    for file in os.listdir(log_file_path):
        if file.endswith(".log"):
            log_file_path = os.path.join(directory, file)
            os.remove(log_file_path)

from __future__ import annotations
import logging.handlers
import os
import logging.config


from .config import APIConfig as _APIConfig, Logging as _Logging


_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGER_NAME = "werkzeug"


def configure_logging(component_name: str, config: _APIConfig) -> None:
    """Configure the logging for the application.

    The component name is written in the log messages to identify the source of the log message.

    The logging configuration is read from a JSON file. If the file is not found, a default configuration is used.
    """
    try:
        log_config = config.logging

        if log_config.console.use:
            _configure_logging_to_console(log_config.console, component_name)
        if log_config.file.use:
            _configure_logging_to_file(log_config.file, component_name)
        logging.getLogger(LOGGER_NAME).setLevel(
            logging.DEBUG
        )  # This ensures the logging level will be fully determined by the handlers
    except ValueError as ve:
        logging.error(f"{component_name}: Configuration error: {ve}")
        raise
    except Exception as e:
        logging.error(f"{component_name}: Error when configuring logging: {e}")
        raise


def _configure_logging_to_console(config: _Logging.HandlerConfig, component_name: str):
    """Configure the logging to the console.

    The console logging is configured to use the logging level and format specified in the configuration.
    """
    handler = logging.StreamHandler()
    handler.setLevel(config.level)
    _add_formatter(handler, component_name)
    _use_handler(handler)


def _configure_logging_to_file(config: _Logging.HandlerConfig, component_name: str) -> None:
    """Configure the logging to a file.

    The file logging is configured to use the logging level and format specified in the configuration.
    """
    if not config.path:
        raise ValueError("Log path is not specified in the configuration. Check the config file.")
    file_path = os.path.join(config.path, _log_file_name(component_name) + ".log")
    handler = logging.handlers.RotatingFileHandler(file_path, maxBytes=10485760, backupCount=5)
    handler.setLevel(config.level)
    _add_formatter(handler, component_name)
    _use_handler(handler)


def _add_formatter(handler: logging.Handler, component_name: str) -> None:
    """Set the formatter for the logging handler."""
    formatter = logging.Formatter(_log_format(component_name), datefmt=_DATE_FORMAT)
    handler.setFormatter(formatter)


def _use_handler(handler: logging.Handler) -> None:
    """Add handler to the logger."""
    logging.getLogger(LOGGER_NAME).addHandler(handler)


def _log_format(component_name: str) -> str:
    log_component_name = "-".join(component_name.lower().split())
    return f"[%(asctime)s.%(msecs)03d] [{log_component_name}] [%(levelname)s]\t %(message)s"


def _log_file_name(component_name: str) -> str:
    return "_".join(component_name.lower().split())

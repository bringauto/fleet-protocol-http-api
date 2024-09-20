from typing import Callable
import logging as _logging
import functools as _functools

from sqlalchemy.exc import OperationalError

from ..logs import LOGGER_NAME
from .connection import (
    get_connection_source as _get_connection_source,
    set_db_connection as _set_db_connection,
)
from .cache import (
    clear_loaded_admins as _clear_loaded_admins,
    clear_connected_cars as _clear_connected_cars
)


_logger = _logging.getLogger(LOGGER_NAME)


def db_access_method(func: Callable) -> Callable:
    """Decorator for the function that restarts the database connection source in case of operational error."""

    @_functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            if isinstance(response, tuple) and len(response) > 1 and response[1] == 500:
                raise Exception
            return response
        except Exception:
            _logger.warning(
                "Restarting connection source due to a probable deletion of database tables."
            )
            _restart_connection_source()
            try:
                return func(*args, **kwargs)
            except OperationalError:
                _logger.error("Database is not accessible.")
                return None

    return wrapper


def _restart_connection_source() -> None:
    _connection_source = _get_connection_source()
    if _connection_source is None:
        _logger.error("Cannot reset connection source if its not currently set.")
    elif _connection_source.url.drivername == "sqlite":
        _logger.info("Using sqlite database stored in memory. No need to reset connection source.")
    else:
        url_obj = _connection_source.url
        host = url_obj.host if url_obj.host is not None else ""
        db_name = url_obj.database if url_obj.database is not None else ""
        password = url_obj.password if url_obj.password is not None else ""
        username = url_obj.username if url_obj.username is not None else ""
        _clear_connected_cars()
        _clear_loaded_admins()
        _set_db_connection(
            dblocation=host,
            port=str(url_obj.port),
            username=username,
            password=password,
            db_name=db_name,
        )

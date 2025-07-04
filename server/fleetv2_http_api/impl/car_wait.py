from __future__ import annotations
from typing import Any
import time
import threading
import logging

from server.logs import LOGGER_NAME

_logger = logging.getLogger(LOGGER_NAME)


class CarWaitObjManager:
    """Manages the wait objects for available cars. Each wait object waits for a response containg newly available car."""

    _default_timeout_ms: int = 5000

    def __init__(self, timeout_ms: int = _default_timeout_ms) -> None:
        _logger.debug(f"Creating CarWaitObjManager with timeout {timeout_ms} ms.")
        CarWaitObjManager._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms
        self._wait_list: list[CarWaitObj] = list()

    @property
    def timeout_ms(self) -> int:
        return self._timeout_ms

    def add_response_content_and_stop_waiting(self, reponse_content: list[Any]) -> None:
        for obj in self._wait_list:
            obj.add_reponse_content_and_stop_waiting(reponse_content)

    def new_wait_obj(self) -> CarWaitObj:
        wait_obj = CarWaitObj(self._timeout_ms)
        self._wait_list.append(wait_obj)
        return wait_obj

    def set_timeout(self, timeout_ms: int) -> None:
        """Set the timeout for wait objects in milliseconds."""
        self._check_nonnegative_timeout(timeout_ms)
        _logger.debug(f"Setting CarWaitObjManager timeout to {timeout_ms} ms.")
        self._timeout_ms = timeout_ms

    def wait_and_get_reponse(self) -> list[Any]:
        wait_obj = self.new_wait_obj()
        reponse = wait_obj.wait_and_get_response()
        self._wait_list.remove(wait_obj)
        return reponse

    @staticmethod
    def _check_nonnegative_timeout(timeout_ms: int) -> None:
        if timeout_ms < 0:
            raise ValueError(f"Timeout must be non-negative, got {timeout_ms}.")


class CarWaitObj:
    """A wait object that waits for a response to be set and then returns it."""

    def __init__(self, timeout_ms: int) -> None:
        self._response_content: list[Any] = list()
        _logger.debug(f"Creating CarWaitObj with timeout {timeout_ms} ms.")
        self._timeout_ms = timeout_ms
        self._condition = threading.Condition()

    def add_reponse_content_and_stop_waiting(self, content: list[Any]) -> None:
        """Set the response content of this wait object and stop waiting."""
        self._response_content = content.copy()
        with self._condition:
            self._condition.notify()

    def wait_and_get_response(self) -> list[Any]:
        """Wait for the response object to be set and then return it."""
        with self._condition:
            self._condition.wait(timeout=self._timeout_ms / 1000)
        return self._response_content

    @staticmethod
    def timestamp() -> int:
        """Unix timestamp in milliseconds."""
        return int(time.time() * 1000)

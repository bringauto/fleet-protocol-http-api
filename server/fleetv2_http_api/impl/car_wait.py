from __future__ import annotations
from typing import List, Any
import time
import threading


class CarWaitObjManager:
    """Manages the wait objects for available cars. Each wait object waits for a response containg newly available car."""

    _default_timeout_ms: int = 5000

    def __init__(self, timeout_ms: int = _default_timeout_ms) -> None:
        CarWaitObjManager._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms
        self._wait_list: list[WaitObj] = list()

    @property
    def timeout_ms(self) -> int: return self._timeout_ms

    def add_response_content_and_stop_waiting(self, reponse_content: List[Any]) -> None:
        for obj in self._wait_list:
            obj.add_reponse_content_and_stop_waiting(reponse_content)

    def new_wait_obj(self) -> WaitObj:
        wait_obj = WaitObj(self._timeout_ms)
        self._wait_list.append(wait_obj)
        return wait_obj

    def set_timeout(self, timeout_ms: int) -> None:
        """Set the timeout for wait objects in milliseconds."""
        self._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms

    def wait_and_get_reponse(self) -> List[Any]:
        wait_obj = self.new_wait_obj()
        reponse = wait_obj.wait_and_get_response()
        self._wait_list.remove(wait_obj)
        return reponse

    @staticmethod
    def _check_nonnegative_timeout(timeout_ms: int) -> None:
        if timeout_ms < 0:
            raise ValueError(f"Timeout must be non-negative, got {timeout_ms}.")


class WaitObj:
    """A wait object that waits for a response to be set and then returns it."""
    def __init__(self, timeout_ms: int) -> None:
        self._response_content: List[Any] = list()
        self._timeout_ms = timeout_ms
        self._condition = threading.Condition()

    def add_reponse_content_and_stop_waiting(self, content: List[Any]) -> None:
        """Set the response content of this wait object and stop waiting."""
        self._response_content = content.copy()
        with self._condition:
            self._condition.notify()

    def wait_and_get_response(self) -> List[Any]:
        """Wait for the response object to be set and then return it."""
        with self._condition:
            self._condition.wait(timeout=self._timeout_ms/1000)
        return self._response_content

    @staticmethod
    def timestamp() -> int:
        """Unix timestamp in milliseconds."""
        return int(time.time()*1000)

from __future__ import annotations
from typing import Dict, List, Any
import time
import threading


class MessageWaitObjManager:

    _default_timeout_ms: int = 5000

    def __init__(self, timeout_ms: int = _default_timeout_ms) -> None:
        MessageWaitObjManager._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms
        self._wait_dict: Dict[str, Dict[str, WaitObj]] = dict()

    @property
    def timeout_ms(self) -> int: return self._timeout_ms

    def add_response_content_and_stop_waiting(self, company: str, car: str, reponse_content: List[Any]) -> None:
        """Make the next wait object in the queue to respond with specified 'reponse_content' and remove it from the queue."""
        if company in self._wait_dict:
            if car in self._wait_dict[company]:
                wait_obj:WaitObj|None = self._wait_dict[company].pop(car)
                if wait_obj is not None:
                    wait_obj.add_reponse_content_and_stop_waiting(reponse_content)

    def new_wait_obj(self, company_name: str, car_name: str) -> WaitObj:
        """Create a new wait object and adds it to the wait queue for given company and car."""
        wait_obj = WaitObj(company_name, car_name, self._timeout_ms)
        if not company_name in self._wait_dict:
            self._wait_dict[company_name] = dict()
        self._wait_dict[company_name][car_name] = wait_obj
        return wait_obj

    def remove_wait_obj(self, wait_obj:WaitObj) -> None:
        """Remove the wait object from the wait queue."""
        company, car = wait_obj.company_name, wait_obj.car_name
        if company in self._wait_dict:
            if car in self._wait_dict[company]:
                self._wait_dict[company].pop(car)
            if not self._wait_dict[company]:
                self._wait_dict.pop(company)

    def set_timeout(self, timeout_ms: int) -> None:
        """Set the timeout for wait objects in milliseconds."""
        self._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms

    def wait_and_get_reponse(self, company_name: str, car_name: str) -> List[Any]:
        """Wait for the next wait object in queue to respond and returns the response content.
        The queue is identified by given company and car."""
        wait_obj = self.new_wait_obj(company_name, car_name)
        reponse = wait_obj.wait_and_get_response()
        self.remove_wait_obj(wait_obj)
        return reponse

    @staticmethod
    def _check_nonnegative_timeout(timeout_ms: int) -> None:
        if timeout_ms < 0:
            raise ValueError(f"Timeout must be non-negative, got {timeout_ms}.")


class WaitObj:
    def __init__(self, company: str, car: str, timeout_ms: int) -> None:
        self._company_name = company
        self._car_name = car
        self._response_content: List[Any] = list()
        self._timeout_ms = timeout_ms
        self._condition = threading.Condition()

    @property
    def company_name(self) -> str: return self._company_name
    @property
    def car_name(self) -> str: return self._car_name

    def add_reponse_content_and_stop_waiting(self, content: List[Any]) -> None:
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

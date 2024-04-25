from __future__ import annotations
from typing import Any
import time
import threading


class MessageWaitObjManager:

    _default_timeout_ms: int = 5000

    def __init__(self, timeout_ms: int = _default_timeout_ms) -> None:
        MessageWaitObjManager._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms
        self._wait_dict: dict[str, dict[str, list[MessageWaitObj]]] = dict()

    @property
    def timeout_ms(self) -> int: return self._timeout_ms

    def add_response_content_and_stop_waiting(self, company: str, car: str, reponse_content: list[Any]) -> None:
        """Make the next wait object in the queue to respond with specified 'reponse_content' and remove it from the queue."""
        wait_objs = self._get_wait_objects_for_given_car(company, car)
        if wait_objs:
            self._send_content_to_all_wait_objs(wait_objs, reponse_content)
            self._remove_wait_obj_list(company, car)

    def new_wait_obj(self, company_name: str, car_name: str) -> MessageWaitObj:
        """Create a new wait object and adds it to the wait queue for given company and car."""
        wait_obj = MessageWaitObj(company_name, car_name, self._timeout_ms)

        if not company_name in self._wait_dict:
            self._wait_dict[company_name] = dict()
        if not car_name in self._wait_dict[company_name]:
            self._wait_dict[company_name][car_name] = list()

        self._wait_dict[company_name][car_name].append(wait_obj)
        return wait_obj

    def remove_wait_obj(self, wait_obj:MessageWaitObj) -> None:
        """Remove the wait object from the wait queue."""
        company, car = wait_obj.company_name, wait_obj.car_name
        if company in self._wait_dict:
            if car in self._wait_dict[company]:
                if wait_obj in self._wait_dict[company][car]:
                    self._wait_dict[company][car].remove(wait_obj)
                if not self._wait_dict[company][car]:
                    self._wait_dict[company].pop(car)
            if not self._wait_dict[company]:
                self._wait_dict.pop(company)

    def set_timeout(self, timeout_ms: int) -> None:
        """Set the timeout for wait objects in milliseconds."""
        self._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms

    def wait_and_get_reponse(self, company_name: str, car_name: str) -> list[Any]:
        """Wait for the next wait object in queue to respond and returns the response content.
        The queue is identified by given company and car."""
        wait_obj = self.new_wait_obj(company_name, car_name)
        reponse = wait_obj.wait_and_get_response()
        self.remove_wait_obj(wait_obj)
        return reponse

    def _send_content_to_all_wait_objs(self, wait_objs: list[MessageWaitObj], reponse_content: list[Any]) -> None:
        for wait_obj in wait_objs:
            wait_obj.add_reponse_content_and_stop_waiting(reponse_content)

    def _get_wait_objects_for_given_car(self, company: str, car: str) -> list[MessageWaitObj]:
        if company in self._wait_dict:
            if car in self._wait_dict[company]:
                return self._wait_dict[company][car]
        return list()

    def _remove_wait_obj_list(self, company: str, car: str) -> None:
        self._wait_dict[company].pop(car)
        if not self._wait_dict[company]:
            self._wait_dict.pop(company)

    @staticmethod
    def _check_nonnegative_timeout(timeout_ms: int) -> None:
        if timeout_ms < 0:
            raise ValueError(f"Timeout must be non-negative, got {timeout_ms}.")


class MessageWaitObj:
    def __init__(self, company: str, car: str, timeout_ms: int) -> None:
        self._company_name = company
        self._car_name = car
        self._response_content: list[Any] = list()
        self._timeout_ms = timeout_ms
        self._condition = threading.Condition()

    @property
    def company_name(self) -> str: return self._company_name
    @property
    def car_name(self) -> str: return self._car_name

    def add_reponse_content_and_stop_waiting(self, content: list[Any]) -> None:
        self._response_content = content.copy()
        with self._condition:
            self._condition.notify()

    def wait_and_get_response(self) -> list[Any]:
        """Wait for the response object to be set and then return it."""
        with self._condition:
            self._condition.wait(timeout=self._timeout_ms/1000)
        return self._response_content

    @staticmethod
    def timestamp() -> int:
        """Unix timestamp in milliseconds."""
        return int(time.time()*1000)

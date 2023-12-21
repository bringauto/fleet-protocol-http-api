from __future__ import annotations
from typing import Dict, List, Any, Optional
import time
import threading


class WaitObjManager:

    def __init__(self, timeout_ms: int = 5000) -> None:
        self._wait_dict = WaitQueueDict()
        self._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms

    @property
    def timeout_ms(self) -> int: return self._timeout_ms

    def is_waiting_for(self, company_name: str, car_name: str) -> bool:
        """Return True if there is any wait object for the given company and car."""
        return self._wait_dict.next_in_queue(company_name, car_name) is not None

    def new_wait_obj(self, company_name: str, car_name: str) -> WaitObj:
        """Create a new wait object and adds it to the wait queue for given company and car."""
        wait_obj = WaitObj(company_name, car_name, self._timeout_ms)
        self._wait_dict.add(company_name, car_name, wait_obj)
        return wait_obj

    def next_in_queue(self, company_name: str, car_name: str) -> Any:
        """Return the next wait object in queue for given company and car."""
        return self._wait_dict.next_in_queue(company_name, car_name)

    def remove_wait_obj(self, wait_obj:WaitObj) -> None:
        """Remove the wait object from the wait queue."""
        queue = self._wait_dict.get_queue(
            wait_obj.company_name,
            wait_obj.car_name
        )
        if queue is None:
            return
        else:
            queue.remove(wait_obj)

    def set_timeout(self, timeout_ms: int) -> None:
        """Set the timeout for wait objects in milliseconds."""
        self._check_nonnegative_timeout(timeout_ms)
        self._timeout_ms = timeout_ms

    def stop_waiting_for(self, company: str, car: str, reponse_content: Optional[List] = None) -> None:
        """Make the next wait object in the queue to respond with specified 'reponse_content' and remove it from the queue."""

        if reponse_content is None:
            reponse_content = list()

        if self._wait_dict.obj_exists(company, car):
            wait_obj:WaitObj|None = self._wait_dict.remove(company, car)
            if wait_obj is not None:
                wait_obj.add_reponse_content(reponse_content)

    def wait_and_get_reponse(self, company_name: str, car_name: str) -> List[Any]:
        """Wait for the next wait object in queue to respond and returns the response content.
        The queue is identified by given company and car."""
        wait_obj = self.new_wait_obj(company_name, car_name)
        reponse = wait_obj.response()
        self.remove_wait_obj(wait_obj)
        return reponse

    def _check_nonnegative_timeout(self, timeout_ms: int) -> None:
        if timeout_ms < 0:
            raise ValueError("timeout_ms must be >= 0 ms")


class WaitQueueDict:

    def __init__(self) -> None:
        self._wait_objs: Dict[str, Dict[str, List[Any]]] = dict()

    def add(self, company_name: str, car_name: str, obj: Optional[Any]=None) -> None:
        queue = self._add_new_queue_if_new_car(company_name, car_name)
        queue.append(obj)

    def get_queue(self, company_name: str, car_name: str) -> List[Any]|None:
        """Return the queue for given company and car.
        If there is no queue, return None."""
        if company_name in self._wait_objs:
            if car_name in self._wait_objs[company_name]:
                return self._wait_objs[company_name][car_name]
        return None

    def next_in_queue(self, company_name: str, car_name: str) -> Any:
        """Return the next object in queue for given company and car."""
        queue = self.get_queue(company_name, car_name)
        if queue is None or not queue:
            return None
        else:
            return queue[0]

    def obj_exists(self, company_name: str, car_name: str) -> bool:
        """Return True if there is any object in queue for given company and car."""
        return (
            company_name in self._wait_objs and
            car_name in self._wait_objs[company_name]
        )

    def remove(self, company_name: str, car_name: str) -> Any:
        """Remove the next object in queue for given company and car and return it."""
        queue = self.get_queue(company_name, car_name)
        if queue is None or not queue:
            return None
        else:
            obj = self._wait_objs[company_name][car_name].pop(0)
            self._remove_empty_dict_part(company_name, car_name)
            return obj

    def _add_new_queue_if_new_car(self, company_name: str, car_name: str) -> List[Any]:
        """Return the queue specified by 'company_name' and 'car_name'.
            Add a new queue for given company and car if there is no queue for it."""
        if company_name not in self._wait_objs:
            self._wait_objs[company_name] = {}
        if car_name not in self._wait_objs[company_name]:
            self._wait_objs[company_name][car_name] = list()
        return self._wait_objs[company_name][car_name]

    def _remove_empty_dict_part(self, company_name: str, car_name: str) -> None:
        if not self._wait_objs[company_name][car_name]:
            self._wait_objs[company_name].pop(car_name)
        if not self._wait_objs[company_name]:
            self._wait_objs.pop(company_name)


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

    def add_reponse_content(self, content: List[Any]) -> None:
        self._response_content = content.copy()
        with self._condition:
            self._condition.notify()

    def response(self) -> List[Any]:
        """Wait for the response object to be set and then return it."""
        with self._condition:
            self._condition.wait(timeout=self._timeout_ms/1000)
        return self._response_content

    @staticmethod
    def timestamp() -> int:
        """Unix timestamp in milliseconds."""
        return int(time.time()*1000)

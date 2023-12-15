# Fleet Protocol v2 HTTP API 
# Copyright (C) 2023 BringAuto s.r.o.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from __future__ import annotations
from typing import Dict, List, Any, Optional


class Wait_Obj_Manager:

    def __init__(self, timeout_ms:int = 5000)->None:
        self.__wait_dict = Wait_Queue_Dict()
        self.__check_nonnegative_timeout(timeout_ms)
        self.__timeout_ms = timeout_ms

    @property
    def timeout_ms(self)->int: return self.__timeout_ms

    def is_waiting_for(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        """Return True if there is any wait object for the given company, car and device id."""
        return self.__wait_dict.next_in_queue(company_name, car_name, sdevice_id) is not None
    
    def new_wait_obj(self, company_name:str, car_name:str, sdevice_id:str)->Wait_Obj:
        """Create a new wait object and adds it to the wait queue for given company, car and device."""
        wait_obj = Wait_Obj(company_name, car_name, sdevice_id, self.__timeout_ms)
        self.__wait_dict.add(company_name, car_name, sdevice_id, wait_obj)
        return wait_obj

    def next_in_queue(self, company_name:str, car_name:str, sdevice_id:str)->Any:
        """Return the next wait object in queue for given company, car and device."""
        return self.__wait_dict.next_in_queue(company_name, car_name, sdevice_id)
    
    def remove_wait_obj(self, wait_obj:Wait_Obj)->None:
        """Remove the wait object from the wait queue."""
        queue = self.__wait_dict.get_queue(
            wait_obj.company_name, 
            wait_obj.car_name, 
            wait_obj.sdevice_id
        )
        if queue is None: return
        else: queue.remove(wait_obj)

    def set_timeout(self, timeout_ms:int)->None:
        """Set the timeout for wait objects in milliseconds."""
        self.__check_nonnegative_timeout(timeout_ms)
        self.__timeout_ms = timeout_ms

    def stop_waiting_for(
        self, 
        company:str, 
        car:str, 
        device:str, 
        reponse_content:Optional[List]=None
        )->None:
        """Make the next wait object in the queue to respond with specified 'reponse_content' and remove it from the queue."""

        if reponse_content is None: reponse_content = list()

        if self.__wait_dict.obj_exists(company, car, device):
            wait_obj:Wait_Obj|None = self.__wait_dict.remove(company, car, device)
            if wait_obj is not None:
                wait_obj.add_reponse_content(reponse_content)

    def wait_and_get_reponse(self, company_name:str, car_name:str, sdevice_id:str)->List[Any]:
        """Wait for the next wait object in queue to respond and returns the response content. 
        The queue is identified by given company, car and device."""
        wait_obj = self.new_wait_obj(company_name, car_name, sdevice_id)
        reponse = wait_obj.response()
        self.remove_wait_obj(wait_obj)
        return reponse

    def __check_nonnegative_timeout(self, timeout_ms:int)->None:
        if timeout_ms < 0: raise ValueError("timeout_ms must be >= 0 ms")


class Wait_Queue_Dict:

    def __init__(self)->None:
        self.__wait_objs:Dict[str, Dict[str, Dict[str, List[Any]]]] = dict()

    def add(self, company_name:str, car_name:str, sdevice_id:str, obj:Optional[Any]=None)->None:
        queue = self.__add_new_queue_if_new_device(company_name, car_name, sdevice_id)
        queue.append(obj)
    
    def get_queue(self, company_name:str, car_name:str, sdevice_id:str)->List[Any]|None:
        """Return the queue for given company, car and device id.
        If there is no queue, return None."""
        if company_name in self.__wait_objs:
            if car_name in self.__wait_objs[company_name]:
                if sdevice_id in self.__wait_objs[company_name][car_name]:
                    return self.__wait_objs[company_name][car_name][sdevice_id]
        return None
    
    def next_in_queue(self, company_name:str, car_name:str, sdevice_id:str)->Any:
        """Return the next object in queue for given company, car and device id."""
        queue = self.get_queue(company_name, car_name, sdevice_id)
        if queue is None or not queue: return None
        else: return queue[0]

    def obj_exists(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        """Return True if there is any object in queue for given company, car and device id."""
        return (
            company_name in self.__wait_objs and
            car_name in self.__wait_objs[company_name] and
            sdevice_id in self.__wait_objs[company_name][car_name]
        )
    
    def remove(self, company_name:str, car_name:str, sdevice_id:str)->Any:
        """Remove the next object in queue for given company, car and device id and return it."""
        queue = self.get_queue(company_name, car_name, sdevice_id)
        if queue is None or not queue: 
            return None
        else:
            obj = self.__wait_objs[company_name][car_name][sdevice_id].pop(0)
            self.__remove_empty_dict_part(company_name, car_name, sdevice_id)
            return obj
    
    def __add_new_queue_if_new_device(self, company_name:str, car_name:str, sdevice_id:str)->List[Any]:
        """Return the queue specified by 'company_name', 'car_name' and 'sdevice_id'. 
            Add a new queue for given company, car and device id if there is no queue for it."""
        if company_name not in self.__wait_objs:
            self.__wait_objs[company_name] = {}
        if car_name not in self.__wait_objs[company_name]:
            self.__wait_objs[company_name][car_name] = dict()
        if sdevice_id not in self.__wait_objs[company_name][car_name]:
            self.__wait_objs[company_name][car_name][sdevice_id] = list()
        return self.__wait_objs[company_name][car_name][sdevice_id]
    
    def __remove_empty_dict_part(self, company_name:str, car_name:str, sdevice_id:str)->None:
        if not self.__wait_objs[company_name][car_name][sdevice_id]: 
            self.__wait_objs[company_name][car_name].pop(sdevice_id)
        if not self.__wait_objs[company_name][car_name]: 
            self.__wait_objs[company_name].pop(car_name)
        if not self.__wait_objs[company_name]: 
            self.__wait_objs.pop(company_name)


import time
class Wait_Obj:
    def __init__(self, company:str, car:str, sdevice_id:str, timeout_ms:int)->None:
        self.__timestamp_ms = Wait_Obj.timestamp()
        self.__company_name = company
        self.__car_name = car
        self.__sdevice_id = sdevice_id
        self.__response_content:List[Any]|None = None
        self.__timeout_ms = timeout_ms

    @property
    def company_name(self)->str: return self.__company_name
    @property
    def car_name(self)->str: return self.__car_name
    @property
    def sdevice_id(self)->str: return self.__sdevice_id

    def add_reponse_content(self, content:List[Any])->None:
        self.__response_content = content.copy()

    def response(self)->List[Any]:
        """Wait for the response object to be set and then return it."""
        while True:
            if self.__response_content is not None: 
                break
            elif self.__timestamp_ms + self.__timeout_ms < Wait_Obj.timestamp(): 
                self.__response_content = list()
                break
        return self.__response_content

    @staticmethod
    def timestamp()->int: 
        """Unix timestamp in milliseconds."""
        return int(time.time()*1000)

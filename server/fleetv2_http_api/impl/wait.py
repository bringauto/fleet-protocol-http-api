from __future__ import annotations
from typing import Dict, List, Any, Optional


class Wait_Manager:

    def __init__(self, timeout_ms:int = 5000)->None:
        self.__wait_dict = Wait_Queue_Dict()
        self.__check_nonnegative_timeout(timeout_ms)
        self.__timeout_ms = timeout_ms

    @property
    def timeout_ms(self)->int: return self.__timeout_ms

    def number_of_waiting_objects(self,company_name:str, car_name:str, sdevice_id:str)->int:
        queue = self.__wait_dict.get_queue(company_name, car_name, sdevice_id)
        if queue is None: return 0
        else: return len(queue)

    def add_wait_obj(self, company_name:str, car_name:str, sdevice_id:str, timestamp_ms:Optional[int]=None)->Wait_Obj:
        wait_obj = Wait_Obj(
            company_name, 
            car_name, 
            sdevice_id, 
            self.__timeout_ms, 
            timestamp_ms
        )
        self.__wait_dict.add(company_name, car_name, sdevice_id, wait_obj)
        return wait_obj

    def is_waiting_for(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        return self.__wait_dict.obj_exists(company_name, car_name, sdevice_id)

    def next_in_queue(self, company_name:str, car_name:str, sdevice_id:str)->Any:
        return self.__wait_dict.next_in_queue(company_name, car_name, sdevice_id)

    def set_timeout(self, timeout_ms:int)->None:
        self.__check_nonnegative_timeout(timeout_ms)
        self.__timeout_ms = timeout_ms

    def stop_waiting_for(
        self, 
        company:str, 
        car:str, 
        device:str, 
        content:Optional[List]=None
        )->None:

        if content is None: content = list()

        if self.__wait_dict.obj_exists(company, car, device):
            wait_obj = self.__wait_dict.remove(company, car, device)
            if wait_obj is not None:
                wait_obj.add_reponse_content(content)

    def wait_for(self, company_name:str, car_name:str, sdevice_id:str)->List[Any]:
        wait_obj = self.add_wait_obj(company_name, car_name, sdevice_id, Wait_Obj.timestamp())
        reponse = wait_obj.response()
        return wait_obj.response()

    def __check_nonnegative_timeout(self, timeout_ms:int)->None:
        if timeout_ms < 0: raise ValueError("timeout_ms must be >= 0 ms")


class Wait_Queue_Dict:

    def __init__(self)->None:
        self.__wait_objs:Dict[str, Dict[str, Dict[str, List[Any]]]] = dict()

    def add(self, company_name:str, car_name:str, sdevice_id:str, obj:Optional[Any]=None)->None:
        queue = self.__add_new_queue_if_new_device(company_name, car_name, sdevice_id)
        queue.append(obj)

    def next_in_queue(self, company_name:str, car_name:str, sdevice_id:str)->Any:
        queue = self.get_queue(company_name, car_name, sdevice_id)
        if queue is None or not queue: return None
        else: return queue[0]
    
    def remove(self, company_name:str, car_name:str, sdevice_id:str)->Any:
        queue = self.get_queue(company_name, car_name, sdevice_id)
        if queue is None or not queue: 
            return None
        else:
            obj = self.__wait_objs[company_name][car_name][sdevice_id].pop(0)
            self.__remove_empty_dict_part(company_name, car_name, sdevice_id)
            return obj

    def obj_exists(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        return (
            company_name in self.__wait_objs and
            car_name in self.__wait_objs[company_name] and
            sdevice_id in self.__wait_objs[company_name][car_name]
        )
    
    def __add_new_queue_if_new_device(self, company_name:str, car_name:str, sdevice_id:str)->List[Any]:
        if company_name not in self.__wait_objs:
            self.__wait_objs[company_name] = {}
        if car_name not in self.__wait_objs[company_name]:
            self.__wait_objs[company_name][car_name] = dict()
        if sdevice_id not in self.__wait_objs[company_name][car_name]:
            self.__wait_objs[company_name][car_name][sdevice_id] = list()
        return self.__wait_objs[company_name][car_name][sdevice_id]
    
    def get_queue(self, company_name:str, car_name:str, sdevice_id:str)->List[Any]|None:
        if company_name in self.__wait_objs:
            if car_name in self.__wait_objs[company_name]:
                if sdevice_id in self.__wait_objs[company_name][car_name]:
                    return self.__wait_objs[company_name][car_name][sdevice_id]
        return None
    
    def __remove_empty_dict_part(self, company_name:str, car_name:str, sdevice_id:str)->None:
        if not self.__wait_objs[company_name][car_name][sdevice_id]: 
            self.__wait_objs[company_name][car_name].pop(sdevice_id)
        if not self.__wait_objs[company_name][car_name]: 
            self.__wait_objs[company_name].pop(car_name)
        if not self.__wait_objs[company_name]: 
            self.__wait_objs.pop(company_name)


import time
class Wait_Obj:
    def __init__(
        self, 
        company_name:str, 
        car_name:str, 
        sdevice_id:str, 
        timeout_ms:int, 
        timestamp_ms:Optional[int]=None,
        )->None:
    
        if timestamp_ms is None: timestamp_ms = Wait_Obj.timestamp()
        self.__timestamp_ms = timestamp_ms
        self.__company_name = company_name
        self.__car_name = car_name
        self.__sdevice_id = sdevice_id
        self.__response_content:List[Any] = list()
        self.__timeout_ms = timeout_ms

    @property
    def timestamp_ms(self)->int: return self.__timestamp_ms
    @property
    def company_name(self)->str: return self.__company_name
    @property
    def car_name(self)->str: return self.__car_name
    @property
    def sdevice_id(self)->str: return self.__sdevice_id

    def add_reponse_content(self, content:List[Any])->None:
        self.__response_content.append(content)

    def response(self)->List[Any]:
        while True:
            if self.__response_content: 
                break
            elif self.__timestamp_ms + self.__timeout_ms < Wait_Obj.timestamp(): 
                break
        return self.__response_content

    @staticmethod
    def timestamp()->int: 
        """Timestamp in milliseconds."""
        return int(time.time()*1000)

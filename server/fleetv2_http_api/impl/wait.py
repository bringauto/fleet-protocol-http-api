from __future__ import annotations
from typing import Dict, List, Any, Optional


class Wait_Manager:

    def __init__(self, timeout_ms:int=1000)->None:
        self.__wait_dict = Wait_Dict()
        self.__wait_objs:List[Wait_Obj] = list()
        if timeout_ms < 0: raise ValueError("timeout_ms must be >= 0 ms")
        self.__timeout_ms = timeout_ms

    @property
    def waiting_for_anything(self)->bool:
        return bool(self.__wait_objs)
    
    def add_wait_obj(self, company_name:str, car_name:str, sdevice_id:str, timestamp_ms:int)->Wait_Obj:
        wait_obj = Wait_Obj(timestamp_ms, company_name, car_name, sdevice_id)
        self.__wait_dict.add(company_name, car_name, sdevice_id, wait_obj)
        self.__insert_into_list(wait_obj)
        return wait_obj

    def check_timeouts(self, curr_time_ms:int)->None:
        while self.__wait_objs:
            oldest =self.__wait_objs[0]
            if self.__timeout(curr_time_ms, oldest): 
                self.__remove_oldest()
            else: 
                break

    def is_waiting_for(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        return self.__wait_dict.wait_obj_exists(company_name, car_name, sdevice_id)

    def set_timeout(self, timeout_ms:int)->None:
        self.__timeout_ms = timeout_ms

    def stop_waiting_for(
        self, 
        company:str, 
        car:str, 
        device:str, 
        content:Optional[List[Any]]=None
        )->None:

        if content is None: 
            content = list()

        if self.__wait_dict.wait_obj_exists(company, car, device):
            wait_obj:Wait_Obj = self.__wait_dict.remove(company, car, device)
            wait_obj.add_reponse_content(content)


    def wait_for(self, company_name:str, car_name:str, sdevice_id:str, curr_timestamp_ms:int)->List[Any]:
        wait_obj = self.add_wait_obj(company_name, car_name, sdevice_id, curr_timestamp_ms)
        return wait_obj.response()

    def __insert_into_list(self, wait_obj:Wait_Obj)->None:
        if not self.__wait_objs: 
            self.__wait_objs.append(wait_obj)
        elif self.__wait_objs[-1].timestamp_ms < wait_obj.timestamp_ms:
            self.__wait_objs.append(wait_obj)
        else:
            self.__insert_into_list(wait_obj)
            k = len(self.__wait_objs)-1
            while k>0 and self.__wait_objs[k].timestamp_ms < wait_obj.timestamp_ms:
                k -= 1
            self.__wait_objs.insert(k, wait_obj)

    def __remove_oldest(self):
        oldest = self.__wait_objs[0]
        self.stop_waiting_for(oldest.company_name, oldest.car_name, oldest.sdevice_id)
        self.__wait_objs.pop(0)

    def __timeout(self, curr_time_ms:int, obj:Wait_Obj)->bool:
        return obj.timestamp_ms + self.__timeout_ms < curr_time_ms
    


class Wait_Dict:

    def __init__(self)->None:
        self.__wait_objs:Dict[str, Dict[str, Dict[str,Any]]] = dict()

    def add(self, company_name:str, car_name:str, sdevice_id:str, obj:Optional[Any]=None)->None:
        if company_name not in self.__wait_objs:
            self.__wait_objs[company_name] = {}
        if car_name not in self.__wait_objs[company_name]:
            self.__wait_objs[company_name][car_name] = dict()
        if sdevice_id not in self.__wait_objs[company_name][car_name]:
            self.__wait_objs[company_name][car_name][sdevice_id] = obj
    
    def remove(self, company_name:str, car_name:str, sdevice_id:str)->Any:
        obj = self.__wait_objs[company_name][car_name].pop(sdevice_id)
        if not self.__wait_objs[company_name][car_name]: 
            self.__wait_objs[company_name].pop(car_name)
        if not self.__wait_objs[company_name]: 
            self.__wait_objs.pop(company_name)
        return obj

    def wait_obj_exists(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        return (
            company_name in self.__wait_objs and
            car_name in self.__wait_objs[company_name] and
            sdevice_id in self.__wait_objs[company_name][car_name]
        )


class Wait_Obj:
    def __init__(self, timestamp_ms:int, company_name:str, car_name:str, sdevice_id:str)->None:
        self.__timestamp_ms = timestamp_ms
        self.__company_name = company_name
        self.__car_name = car_name
        self.__sdevice_id = sdevice_id
        self.__response_content:List[Any] = list()

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
            if self.__response_content: break
        return self.__response_content
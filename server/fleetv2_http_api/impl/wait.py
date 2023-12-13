from typing import Dict, List
import dataclasses


class Wait_Dict:

    def __init__(self)->None:
        self.__wait_objs:Dict[str, Dict[str, List[str]]] = dict()

    def is_waiting_for(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        return (
            company_name in self.__wait_objs and
            car_name in self.__wait_objs[company_name] and
            sdevice_id in self.__wait_objs[company_name][car_name]
        )
    
    def remove(self, company_name:str, car_name:str, sdevice_id:str)->None:
        self.__wait_objs[company_name][car_name].remove(sdevice_id)
        if not self.__wait_objs[company_name][car_name]: self.__wait_objs[company_name].pop(car_name)
        if not self.__wait_objs[company_name]: self.__wait_objs.pop(company_name)
        
    def add(self, company_name:str, car_name:str, sdevice_id:str)->None:
        if company_name not in self.__wait_objs:
            self.__wait_objs[company_name] = {}
        if car_name not in self.__wait_objs[company_name]:
            self.__wait_objs[company_name][car_name] = list()
        if sdevice_id not in self.__wait_objs[company_name][car_name]:
            self.__wait_objs[company_name][car_name].append(sdevice_id)


@dataclasses.dataclass(frozen=True)
class Wait_Obj:
    timestamp_ms:int
    company_name:str
    car_name:str
    sdevice_id:str


class Wait_Manager:

    def __init__(self, timeout_ms:int=1000)->None:
        self.__wait_dict = Wait_Dict()
        if timeout_ms < 0: raise ValueError("timeout_ms must be >= 0 ms")
        self.__timeout_ms = timeout_ms
        self.__wait_objs:List[Wait_Obj] = list()

    @property
    def waiting_for_anything(self)->bool:
        return bool(self.__wait_objs)

    def check_timeouts(self, curr_time_ms:int)->None:
        while self.__wait_objs:
            oldest =self.__wait_objs[0]
            if self.__timeout(curr_time_ms, oldest): 
                self.__remove_oldest()
            else: 
                break

    def is_waiting_for(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        return self.__wait_dict.is_waiting_for(company_name, car_name, sdevice_id)
    
    def set_timeout(self, timeout_ms:int)->None:
        self.__timeout_ms = timeout_ms

    def stop_waiting_for(self, company_name:str, car_name:str, sdevice_id:str)->None:
        self.__wait_dict.remove(company_name, car_name, sdevice_id)
    
    def wait_for(self, company_name:str, car_name:str, sdevice_id:str, timestamp_ms:int)->None:
        self.__wait_dict.add(company_name, car_name, sdevice_id)
        wait_obj = Wait_Obj(timestamp_ms, company_name, car_name, sdevice_id)
        self.__insert_into_list(wait_obj)

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
    


from typing import Dict, List


__device_ids:Dict[str,Dict[int,List[str]]] = {}


def device_ids()->Dict[str,Dict[int,List[str]]]:
    return __device_ids.copy()


def clear_device_ids()->None:
    __device_ids.clear()


def store_device_id_if_new(car_info:str, module_id:int, serialized_device_id:str)->bool:
    serialized_device_id = serialized_device_id
    car_info = car_info
    if car_info not in __device_ids:
        __device_ids[car_info] = dict()
    if module_id not in __device_ids[car_info]:
        __device_ids[car_info][module_id] = list()
    if serialized_device_id not in __device_ids[car_info][module_id]:
        __device_ids[car_info][module_id] = [serialized_device_id]
        return True
    return False


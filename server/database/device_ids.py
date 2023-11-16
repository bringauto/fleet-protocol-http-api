from typing import Dict, List
from copy import deepcopy


Device_Ids = Dict[str,Dict[str, Dict[int,List[str]]]]


__device_ids:Device_Ids = {}


def device_ids()->Device_Ids:
    """Return a deep copy of the device_ids dictionary."""""
    return deepcopy(__device_ids)


def clear_device_ids()->None:
    """Clear the whole device_ids dictionary."""""
    __device_ids.clear()


def remove_device_id(company_name:str, car_name:str, module_id:int, serialized_device_id:str)->None:
    """Remove a device id from its module dict in the device_ids dictionary."""
    __device_ids[company_name][car_name][module_id].remove(serialized_device_id)


def clean_up_disconnected_cars_and_modules()->None:
    """Remove empty modules, cars and companies from the device_ids dictionary."""
    for company_name in __device_ids:
        for car_name in __device_ids[company_name]:
            empty_modules = [module_id for module_id in __device_ids[company_name][car_name].keys() if __device_ids[company_name][car_name][module_id]==[]]
            for module_id in empty_modules:
                __device_ids[company_name][car_name].pop(module_id)

        cars_without_modules = [car for car in __device_ids[company_name].keys() if not __device_ids[company_name][car]]
        for car in cars_without_modules:
            __device_ids[company_name].pop(car)

    companies_without_cars = [company for company in __device_ids.keys() if not __device_ids[company]]
    for company in companies_without_cars:
            __device_ids.pop(company)


def store_device_id_if_new(company_name:str, car_name:str, module_id:int, serialized_device_id:str)->bool:
    """
    Add a device id to the device_ids dictionary if it is not already there.
    Returns True if the device id was stored, False otherwise.
    """
    serialized_device_id = serialized_device_id
    if company_name not in __device_ids:
        __device_ids[company_name] = dict()

    if car_name not in __device_ids[company_name]:
        __device_ids[company_name][car_name] = dict()

    if module_id not in __device_ids[company_name][car_name]:
        __device_ids[company_name][car_name][module_id] = list()

    if serialized_device_id not in __device_ids[company_name][car_name][module_id]:
        __device_ids[company_name][car_name][module_id] = [serialized_device_id]
        return True
    
    return False


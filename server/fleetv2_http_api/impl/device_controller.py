from __future__ import annotations


from typing import List, Optional, Tuple

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Message
from database.database_controller import list_messages, send_messages_to_database, Message_DB
from database.device_ids import store_device_id_if_new, device_ids
from database.time import timestamp


def __message_from_db(message_db:Message_DB)->Message:
    return Message(
        timestamp=message_db.timestamp,
        id=DeviceId(
            message_db.module_id, 
            message_db.device_type, 
            message_db.device_role, 
            message_db.device_name
        ),
        payload=Payload(
            type=message_db.message_type, 
            encoding=message_db.payload_encoding,
            data=message_db.payload_data
        )
    )

    
def available_cars()->List[str]:
    return list(device_ids().keys())


def available_devices(company_name:str, car_name:str, module_id:Optional[int]=None)->List[str]:  # noqa: E501
    car = _serialized_car_info(company_name, car_name)
    if car not in device_ids(): 
        return [], 404 # type: ignore
    if module_id is None: 
        return __all_available_devices(car)
    else: 
        return __available_devices_for_module(car, module_id)


def list_commands(
    company_name:str, 
    car_name:str, 
    device_id:DeviceId, 
    all=None, 
    since=None
    )->Tuple[List[Message], int]:  # noqa: E501

    commands = [__message_from_db(m) for m in list_messages(
        company_name=company_name,
        car_name=car_name,
        message_type=1,
        module_id=device_id.module_id,
        device_type=device_id.type,
        device_role=device_id.role,
        all=all, since=since
    )]
    if commands: return commands, 200
    else: return [], 404


def list_statuses(
    company_name:str, 
    car_name:str, 
    device_id:DeviceId, 
    all=None, 
    since:Optional[int]=None
    )->Tuple[List[Message], int]:  # noqa: E501

    statuses = [__message_from_db(m) for m in list_messages(
        company_name=company_name,
        car_name=car_name,
        message_type=0,
        module_id=device_id.module_id,
        device_type=device_id.type,
        device_role=device_id.role,
        all=all, since=since
    )]
    if statuses: return statuses, 200
    else: return [], 404
    

def send_commands(company_name:str, car_name:str, device_id:DeviceId, payload:List[Payload]=list())->Tuple[str, int]:  # noqa: E501
    car = _serialized_car_info(company_name, car_name)
    if car not in device_ids():
        return "", 404
    elif device_id.module_id not in device_ids()[car]:
        return "", 404
    else:
        tstamp = timestamp()
        commands_to_db = [
            Message_DB(
                timestamp=tstamp,
                module_id=device_id.module_id,
                device_type=device_id.type,
                device_role=device_id.role,
                device_name=device_id.name,
                message_type=1,
                payload_encoding=p.encoding,
                payload_data=p.data # type: ignore
            ) 
            for p in payload
        ]
        send_messages_to_database(company_name, car_name, *commands_to_db)
        return "", 200


def send_statuses(company_name:str, car_name:str, device_id:DeviceId, payload:List[Payload]=list())->Tuple[str,int]:  # noqa: E501
    tstamp = timestamp()
    statuses_to_db = [
        Message_DB(
            timestamp=tstamp,
            module_id=device_id.module_id,
            device_type=device_id.type,
            device_role=device_id.role,
            device_name=device_id.name,
            message_type=0,
            payload_encoding=p.encoding,
            payload_data=p.data # type: ignore
        ) 
        for p in payload
    ]

    send_messages_to_database(company_name, car_name, *statuses_to_db)
    store_device_id_if_new(
        car_info = _serialized_car_info(company_name, car_name), 
        module_id = device_id.module_id, 
        serialized_device_id = _serialized_device_id(device_id)
    )
    return "", 200


def _serialized_car_info(company_name:str, car_name:str)->str:
    return f"{company_name}_{car_name}"

def _serialized_device_id(device_id:DeviceId)->str:
    return f"{device_id.module_id}_{device_id.type}_{device_id.role}"



def __all_available_devices(car_info:str)->List[str]:
    device_id_list:List[str] = list()
    for module_devices in device_ids()[car_info].values():
        device_id_list.extend(module_devices)
    return device_id_list

def __available_devices_for_module(car_info:str, module_id:int)->List[str]:
    if not module_id in device_ids()[car_info]: 
        return [], 404 # type: ignore
    else: 
        return device_ids()[car_info][module_id]



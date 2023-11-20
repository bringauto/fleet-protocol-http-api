from __future__ import annotations


from typing import List, Optional, Tuple

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Message
from database.database_controller import send_messages_to_database, Message_DB, _deserialize_device_id
from database.database_controller import list_messages as __list_messages
from database.device_ids import store_device_id_if_new, device_ids
from database.database_controller import cleanup_device_commands_and_warn_before_future_commands

from enums import MessageType

       
def available_cars()->List[str]:
    cars:List[str] = list()
    device_dict = device_ids()
    for company_name in device_dict:
        for car_name in device_dict[company_name]:
            cars.append(_serialized_car_info(company_name, car_name))
    return cars


def available_devices(company_name:str, car_name:str, module_id:Optional[int]=None)->List[str]:  # noqa: E501
    device_dict = device_ids()
    if company_name not in device_dict:
        return [], 404 # type: ignore
    
    elif car_name not in device_dict[company_name]:
        return [], 404 # type: ignore
    
    if module_id is None: 
        return __all_available_devices(company_name, car_name)
    else: 
        return __available_devices_for_module(company_name, car_name, module_id)


def list_commands(
    company_name:str, 
    car_name:str, 
    sdevice_id:str, 
    all:Optional[str]=None, 
    since:Optional[int]=None
    )->Tuple[List[Message], int]:  # noqa: E501

    commands = [__message_from_db(m) for m in __list_messages(
        company_name=company_name,
        car_name=car_name,
        message_type=MessageType.COMMAND_TYPE,
        serialized_device_id=sdevice_id,
        all=all, 
        since=since
    )]

    return commands, 200


def list_statuses(
    company_name:str, 
    car_name:str, 
    sdevice_id:str, 
    all:Optional[str]=None, 
    since:Optional[int]=None
    )->Tuple[List[Message], int]:  # noqa: E501

    print(sdevice_id, all, since)

    statuses = [__message_from_db(m) for m in __list_messages(
        company_name=company_name,
        car_name=car_name,
        message_type=MessageType.STATUS_TYPE,
        serialized_device_id=sdevice_id,
        all=all, 
        since=since
    )]
    return statuses, 200


def send_commands(company_name:str, car_name:str, sdevice_id:str, messages:List[Message]=list())->Tuple[str, int]:  # noqa: E501
    device_dict = device_ids()
    path_module_id, path_device_type, path_device_role = _deserialize_device_id(sdevice_id)

    __check_corresponding_device_id_in_path_and_messages(
        path_module_id, 
        path_device_type, 
        path_device_role, 
        sdevice_id, 
        *messages
    )
 
    if company_name not in device_dict:
        return [], 404 # type: ignore
    
    elif car_name not in device_dict[company_name]:
        return [], 404 # type: ignore
    
    elif path_module_id not in device_dict[company_name][car_name]:
        return "", 404
    else:
        commands_to_db = [
            Message_DB(
                timestamp=message.timestamp,
                serialized_device_id=sdevice_id,
                module_id=message.id.module_id,
                device_type=message.id.type,
                device_role=message.id.role,
                device_name=message.id.name,
                message_type=MessageType.COMMAND_TYPE,
                payload_encoding=message.payload.encoding,
                payload_data=message.payload.data # type: ignore
            ) 
            for message in messages
        ]
        send_messages_to_database(company_name, car_name, *commands_to_db)
        return "", 200


def send_statuses(
    company_name:str, 
    car_name:str, 
    sdevice_id:str, 
    messages:List[Message]=list()
    )->Tuple[str|List[str],int]:  # noqa: E501

    path_module_id, path_device_type, path_device_role, = _deserialize_device_id(sdevice_id)
    __check_corresponding_device_id_in_path_and_messages(
        path_module_id,
        path_device_type,
        path_device_role,
        sdevice_id,
        *messages
    )

    statuses_to_db = [
        Message_DB(
            timestamp=message.timestamp,
            serialized_device_id=sdevice_id,
            module_id=path_module_id,
            device_type=message.id.type,
            device_role=message.id.role,
            device_name=message.id.name,
            message_type=MessageType.STATUS_TYPE,
            payload_encoding=message.payload.encoding,
            payload_data=message.payload.data # type: ignore
        ) 
        for message in messages
    ]
    send_messages_to_database(company_name, car_name, *statuses_to_db)
    first_status_was_sent = store_device_id_if_new(
        company_name = company_name,
        car_name = car_name,
        module_id = path_module_id, 
        serialized_device_id = sdevice_id
    )
    if first_status_was_sent: 
        return __handle_first_status_and_return_warnings(
            timestamp = messages[-1].timestamp, 
            company_name = company_name, 
            car_name = car_name, 
            serialized_device_id=sdevice_id
        ), 200

    return "", 200


def _serialized_device_id(device_id:DeviceId)->str:
    return f"{device_id.module_id}_{device_id.type}_{device_id.role}"


def __check_corresponding_device_id_in_path_and_messages(
    path_module_id:int, 
    path_device_type:int, 
    path_device_role:str,
    serialized_device_id:str,
    *messages:Message
    )->None:

    for message in messages:
        if message.id.module_id != path_module_id or \
            message.id.type != path_device_type or \
            message.id.role != path_device_role:
            raise ValueError(
                f"The device Id in path (.../{serialized_device_id}) is not equal "
                f"to a device Id from the message ({_serialized_device_id(message.id)})"
            )
    

def _serialized_car_info(company_name:str, car_name:str)->str:
    return f"{company_name}_{car_name}"


def __all_available_devices(company_name:str, car_name:str)->List[str]:
    device_id_list:List[str] = list()
    for module_devices in device_ids()[company_name][car_name].values():
        device_id_list.extend(module_devices)
    return device_id_list

def __available_devices_for_module(company_name:str, car_name:str, module_id:int)->List[str]:
    if not module_id in device_ids()[company_name][car_name]: 
        return [], 404 # type: ignore
    else: 
        return device_ids()[company_name][car_name][module_id]


def __handle_first_status_and_return_warnings(
    timestamp:int, 
    company_name:str,
    car_name:str,
    serialized_device_id:str,
    )->List[str]:

    return cleanup_device_commands_and_warn_before_future_commands(
        current_timestamp = timestamp, 
        company_name = company_name,
        car_name = car_name,
        serialized_device_id=serialized_device_id
    )
  
def __message_from_db(message_db:Message_DB)->Message:
    return Message(
        timestamp=message_db.timestamp,
        id=DeviceId(
            message_db.module_id, 
            message_db.device_type, 
            message_db.device_role
        ),
        payload=Payload(
            type=message_db.message_type, 
            encoding=message_db.payload_encoding,
            data=message_db.payload_data
        )
    )


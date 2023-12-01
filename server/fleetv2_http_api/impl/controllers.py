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


from typing import List, Optional, Tuple, Dict

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Message
from fleetv2_http_api.models.module import Module
from database.database_controller import send_messages_to_database, Message_DB
from database.database_controller import list_messages as __list_messages
from database.device_ids import store_device_id_if_new, device_ids, serialized_device_id
from database.database_controller import cleanup_device_commands_and_warn_before_future_commands
from enums import MessageType

       
def available_cars()->List[str]:
    """Return a list of serialized car info for cars owning at least one available device."""
    cars:List[str] = list()
    device_dict = device_ids()
    for company_name in device_dict:
        for car_name in device_dict[company_name]:
            cars.append(_serialized_car_info(company_name, car_name))
    return cars


def available_devices(company_name:str, car_name:str, module_id:Optional[int]=None)->Module|List[Module]:  # noqa: E501
    """Return a list of serialized device ids for devices available in a given car.
    If a module_id is not specified, return all available devices in a given car.
    """
    device_dict = device_ids()
    if company_name not in device_dict:
        return [], 404 # type: ignore
    
    elif car_name not in device_dict[company_name]:
        return [], 404 # type: ignore
    
    if module_id is None: 
        car_modules = device_dict[company_name][car_name]
        return [__available_module(company_name, car_name, id) for id in car_modules] # type: ignore
    else: 
        if module_id not in device_dict[company_name][car_name]: 
            return 404 # type: ignore
        else:
            return __available_module(company_name, car_name, module_id) # type: ignore


def list_commands(
    company_name:str, 
    car_name:str, 
    sdevice_id:str, 
    all_available:Optional[str]=None, 
    until:Optional[int]=None
    )->Tuple[List[Message], int]:  # noqa: E501
    """Return list containing the OLDEST command currently stored for an AVAILABLE device. 
    If a device is not available, return empty list and code 404.

    If 'all_available' is not None, return ALL commands stored for a given device.
    If 'until' is specified (unix timestamp in milliseconds), return all stored commands
    having the timestamp equal or lower than 'until'.
    """

    if company_name not in device_ids(): return [], 404 # type: ignore
    elif car_name not in device_ids()[company_name]: return [], 404 # type: ignore

    commands = [__message_from_db(m) for m in __list_messages(
        company_name=company_name,
        car_name=car_name,
        message_type=MessageType.COMMAND_TYPE,
        serialized_device_id=sdevice_id,
        all_available=all_available, 
        limit_timestamp=until
    )]

    return commands, 200


def list_statuses(
    company_name:str, 
    car_name:str, 
    sdevice_id:str, 
    all_available:Optional[str]=None, 
    since:Optional[int]=None
    )->Tuple[List[Message], int]:  # noqa: E501

    """Return list containing the NEWEST status currently stored for an AVAILABLE device. 
    If a device is not available, return empty list and code 404.

    If 'all_available' is not None, return ALL statuses stored for a given device.
    If 'since' is specified (unix timestamp in milliseconds), return all stored statuses
    having the timestamp equal or lower than 'since'.
    """

    if company_name not in device_ids(): return [], 404 # type: ignore
    elif car_name not in device_ids()[company_name]: return [], 404 # type: ignore

    statuses = [__message_from_db(m) for m in __list_messages(
        company_name=company_name,
        car_name=car_name,
        message_type=MessageType.STATUS_TYPE,
        serialized_device_id=sdevice_id,
        all_available=all_available, 
        limit_timestamp=since
    )]
    return statuses, 200


def send_commands(
    company_name:str, 
    car_name:str, 
    sdevice_id:str, 
    messages:List[Message] = [],
    body:List[Dict] = []
    )->Tuple[str, int]:  # noqa: E501

    """Send a list of commands to given device. If the device specified is not available,
    return code 404.

    The body of the request should contain a list of commands, each in the form of a dictionary.

    If for any command the device_id does not correspond to the sdevice_id, exception is raised.
    """

    device_dict = device_ids()
    messages.extend([Message.from_dict(b) for b in body])
    __check_messages(MessageType.COMMAND_TYPE, sdevice_id, *messages)
 
    if company_name not in device_dict:
        return [], 404 # type: ignore
    
    elif car_name not in device_dict[company_name]:
        return "", 404
    
    elif messages[-1].device_id.module_id not in device_dict[company_name][car_name]:
        return "", 404

    else:
        commands_to_db = [
            Message_DB(
                timestamp=message.timestamp,
                serialized_device_id=sdevice_id,
                module_id=message.device_id.module_id,
                device_type=message.device_id.type,
                device_role=message.device_id.role,
                device_name=message.device_id.name,
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
    messages:List[Message] = [],
    body:List[Dict] = []
    )->Tuple[str|List[str],int]:  # noqa: E501

    """Send a list of statuses to given device. 
    The device specified in the statuses is then automatically considered available.

    The body of the request should contain a list of statuses, each in the form of a dictionary.

    If for any status the device_id does not correspond to the sdevice_id, exception is raised.
    """

    messages.extend([Message.from_dict(b) for b in body])
    if messages == []: return "", 200
    __check_messages(MessageType.STATUS_TYPE, sdevice_id, *messages)

    statuses_to_db = [
        Message_DB(
            timestamp=message.timestamp,
            serialized_device_id=sdevice_id,
            module_id=message.device_id.module_id,
            device_type=message.device_id.type,
            device_role=message.device_id.role,
            device_name=message.device_id.name,
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
        device_id = messages[-1].device_id
    )
    if first_status_was_sent: 
        return __handle_first_status_and_return_warnings(
            timestamp = messages[-1].timestamp, 
            company_name = company_name, 
            car_name = car_name, 
            serialized_device_id=sdevice_id
        ), 200

    return "", 200


class SendingCommandAsStatus(Exception): pass
class SendingStatusAsCommand(Exception): pass


def _serialized_car_info(company_name:str, car_name:str)->str:
    return f"{company_name}_{car_name}"


def __check_messages(
    expected_message_type:int,
    sdevice_id:str,
    *messages:Message
    )->None:

    __check_message_types(expected_message_type, *messages)
    __check_equal_device_id_in_path_and_messages(sdevice_id, *messages)

def __check_message_types(expected_message_type:int, *messages:Message)->None:
    """Check that type of every message matches the method (send command or send status)."""
    for message in messages:
        if message.payload.type != expected_message_type:
            if expected_message_type == MessageType.COMMAND_TYPE:
                raise SendingStatusAsCommand(
                    f"Cannot send a status as a command: {message}"
                )
            else:
                raise SendingCommandAsStatus(
                    f"Cannot send a command as a status: {message}"
                )

def __check_equal_device_id_in_path_and_messages(
    sdevice_id:str,
    *messages:Message  
    )->None:

    for message in messages:
        sdevice_id_from_message = serialized_device_id(message.device_id)
        if sdevice_id_from_message != sdevice_id:
            raise Unmatched_Device_Ids_In_Argument_And_Message(
                f"The device Id in path (.../{sdevice_id}) is not equal "
                f"to a device Id from the message ({sdevice_id_from_message})"
            )


def __available_module(company_name:str, car_name:str, module_id:int)->Module:
    device_id_list = list((device_ids()[company_name][car_name][module_id]).values())
    return Module(module_id, device_id_list)


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
        device_id=DeviceId(
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


class Unmatched_Device_Ids_In_Argument_And_Message(Exception): pass

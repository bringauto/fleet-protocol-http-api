from __future__ import annotations
from typing import List, Optional, Tuple, Dict
from enums import MessageType

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Message
from fleetv2_http_api.models.module import Module
from fleetv2_http_api.models.car import Car
from database.database_controller import (
    send_messages_to_database,
    Message_DB,
    cleanup_device_commands_and_warn_before_future_commands
)
from database.database_controller import list_messages as _list_messages
from database.device_ids import store_device_id_if_new, device_ids, serialized_device_id
from fleetv2_http_api.impl.wait import WaitObjManager


_status_wait_manager = WaitObjManager()
def set_status_wait_timeout_s(timeout_s: float) -> None:
    _status_wait_manager.set_timeout(int(1000*timeout_s))

def get_status_wait_timeout_s() -> float:
    return _status_wait_manager.timeout_ms*0.001

_command_wait_manager = WaitObjManager()
def set_command_wait_timeout_s(timeout_s: float) -> None:
    _command_wait_manager.set_timeout(int(1000*timeout_s))

def get_command_wait_timeout_s() -> float:
    return _command_wait_manager.timeout_ms*0.001


def available_cars() -> List[Car]:
    """Return a list of serialized car info for cars owning at least one available device."""
    cars: List[Car] = list()
    device_dict = device_ids()
    for company_name in device_dict:
        for car_name in device_dict[company_name]:
            cars.append(Car(company_name, car_name))
    return cars


def available_devices(
    company_name: str,
    car_name: str,
    module_id: Optional[int] = None
    ) -> Tuple[Module|List[Module], int]:  # noqa: E501

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
        return [_available_module(company_name, car_name, id) for id in car_modules], 200
    else:
        if module_id not in device_dict[company_name][car_name]:
            return [], 404 # type: ignore
        else:
            return _available_module(company_name, car_name, module_id), 200


def list_commands(
    company_name: str,
    car_name: str,
    all_available: Optional[str] = None,
    since: Optional[int] = None,
    wait: Optional[str] = None
    ) -> Tuple[List[Message], int]:  # noqa: E501

    """Return list containing the NEWEST command currently stored for an AVAILABLE device.
    If a device is not available, return empty list and code 404.

    If 'all_available' is not None, return ALL commands stored for a given device.
    If 'since' is specified (unix timestamp in milliseconds), return all stored commands
    having the timestamp equal or greater than 'since'.
    The 'wait' parameter makes the function to wait for available commands, if at the moment of request,
    there are no commands available. If 'wait' is None, the function will immediatelly
    return an empty list.
    """

    db_commands = _list_messages(
        company_name,
        car_name,
        MessageType.COMMAND_TYPE,
        all_available,
        since
    )

    if db_commands or wait is None:
        msg, code = _check_car_availability(company_name, car_name)
        if code == 200:
            # device is available and has commands, return them
            return [_message_from_db(m) for m in db_commands], 200
        else:
            return [], code # type: ignore
    else:
        awaited_commands: List[Message] = _command_wait_manager.wait_and_get_reponse(company_name, car_name)
        if awaited_commands:
            if since is not None and awaited_commands[-1].timestamp > since:
                return [], 200
            return awaited_commands, 200
        else:
            if company_name not in device_ids():
                return [], 404 # type: ignore
            elif car_name not in device_ids()[company_name]:
                return [], 404 # type: ignore
            return [], 200


def list_statuses(
    company_name: str,
    car_name: str,
    all_available: Optional[str] = None,
    wait: Optional[str] = None,
    since: Optional[int] = None
    ) -> Tuple[List[Message], int]:  # noqa: E501

    """Return list containing the NEWEST status currently stored for an AVAILABLE device.
    If a device is not available, return empty list and code 404.

    If 'all_available' is not None, return ALL statuses stored for a given device.
    If 'since' is specified (unix timestamp in milliseconds), return all stored statuses
    having the timestamp equal or lower than 'since'.
    The 'wait' parameter makes the function to wait for available statuses, if at the moment of request,
    there are no statuses available. If 'wait' is None, the function will immediatelly
    return an empty list.
    """

    db_statuses = _list_messages(
        company_name,
        car_name,
        MessageType.STATUS_TYPE,
        all_available,
        since
    )

    if db_statuses:
        return [_message_from_db(m) for m in db_statuses], 200
    elif wait is None:
        # no statuses mean device is unavailable and not found
        return [], 404
    else:
        awaited_statuses: List[Message] = _status_wait_manager.wait_and_get_reponse(company_name, car_name)
        if awaited_statuses:
            if since is not None and awaited_statuses[-1].timestamp < since:
                return [], 200
            else:
                return awaited_statuses, 200
        else:
            return [], 404


def send_commands(
    company_name: str,
    car_name: str,
    messages: Optional[List[Message]] = None,
    body: List[Dict] = []
    ) -> Tuple[str, int]:  # noqa: E501

    """Send a list of commands to given device. If the device specified is not available,
    return code 404.

    The body of the request should contain a list of commands, each in the form of a dictionary.

    If for any command the device_id does not correspond to the sdevice_id, exception is raised.
    """
    if messages is None:
        messages = []
    messages.extend([Message.from_dict(b) for b in body])
    if len(messages) == 0:
        return "", 200
    msg, code = _check_sent_commands(company_name, car_name, messages)
    if msg.strip()!="":
        return msg, code
    assert messages is not None

    _command_wait_manager.stop_waiting_for(company_name, car_name, reponse_content=messages)
    commands_to_db = _message_db_list(messages, MessageType.COMMAND_TYPE)
    return send_messages_to_database(company_name, car_name, *commands_to_db)


def send_statuses(
    company_name: str,
    car_name: str,
    messages: Optional[List[Message]] = None,
    body: List[Dict] = []
    ) -> Tuple[str|List[str],int]:  # noqa: E501

    """Send a list of statuses to given device.
    The device specified in the statuses is then automatically considered available.
    """

    if messages is None:
        messages = []
    messages.extend([Message.from_dict(b) for b in body])
    if messages == []:
        return "", 200
    errors = _check_messages(MessageType.STATUS_TYPE, *messages)
    if errors[0] != "":
        return errors

    _status_wait_manager.stop_waiting_for(company_name, car_name, reponse_content=messages)
    response_msg = send_messages_to_database(company_name, car_name, *_message_db_list(messages, MessageType.STATUS_TYPE))
    cmd_warnings = _check_and_handle_first_status(company_name, car_name, messages)
    return response_msg[0] + cmd_warnings, response_msg[1]


def _available_module(company_name: str, car_name: str, module_id: int) -> Module:
    device_id_list = list((device_ids()[company_name][car_name][module_id]).values())
    return Module(module_id, device_id_list)

def _check_and_handle_first_status(company: str, car: str, messages: List[Message]) -> str:
    first_status_was_sent = store_device_id_if_new(company,car,messages[-1].device_id)
    command_removal_warnings = ""
    sdevice_id = serialized_device_id(messages[-1].device_id)
    if first_status_was_sent:
        command_removal_warnings = "\n".join(_handle_first_status_and_return_warnings(
            messages[-1].timestamp,
            company,
            car,
            sdevice_id
        ))
    if command_removal_warnings.strip() != "":
        command_removal_warnings =  "\n\n" + command_removal_warnings
    return command_removal_warnings

def _check_sent_commands(company_name: str, car_name: str, messages: List[Message]) -> Tuple[str, int]:
    errors, code = _check_messages(MessageType.COMMAND_TYPE, *messages)
    if errors != "" or code != 200:
        return errors, code
    module_id = messages[0].device_id.module_id
    sdevice_id = serialized_device_id(messages[0].device_id)
    return _check_device_availability(company_name, car_name, module_id, sdevice_id)

def _check_messages(
    expected_message_type: str,
    *messages: Message
    ) -> Tuple[str, int]:

    errors: str = ""
    errors = _check_message_types(expected_message_type, *messages)

    if not errors.strip()=="":
        return errors, 500
    else:
        return "", 200

def _check_message_types(expected_message_type: str, *messages: Message) -> str:
    """Check that type of every message matches the method (send command or send status)."""
    for message in messages:
        if message.payload.message_type != expected_message_type:
            if expected_message_type == MessageType.COMMAND_TYPE:
                return f"Cannot send a status as a command: {message}"
            else:
                return f"Cannot send a command as a status: {message}"
    return ""

def _check_device_availability(company_name: str, car_name: str, module_id: int, sdevice_id: str) -> Tuple[str, int]:
    device_dict = device_ids()
    if company_name not in device_dict:
        return f"No car is available under a company '{company_name}'.", 404 # type: ignore
    elif car_name not in device_dict[company_name]:
        return f"Car named '{car_name}' is not available under a company '{company_name}'.", 404

    elif module_id not in device_dict[company_name][car_name]:
        return \
            f"No module with id '{module_id}' is available in car " \
            f"'{car_name}' under the company '{company_name}'", 404
    elif sdevice_id not in device_dict[company_name][car_name][module_id]:
        return \
            f"No device with id '{sdevice_id}' is available in module " \
            f"'{module_id}' in car '{car_name}' under the company '{company_name}'", 404
    else:
        return "", 200

def _check_car_availability(company_name: str, car_name: str) -> Tuple[str, int]:
    device_dict = device_ids()
    if company_name not in device_dict:
        return f"No car is available under a company '{company_name}'.", 404 # type: ignore
    elif car_name not in device_dict[company_name]:
        return f"Car named '{car_name}' is not available under a company '{company_name}'.", 404
    else:
        return "", 200

def _handle_first_status_and_return_warnings(
    timestamp: int,
    company_name: str,
    car_name: str,
    serialized_device_id: str,
    ) -> List[str]:

    return cleanup_device_commands_and_warn_before_future_commands(
        current_timestamp = timestamp,
        company_name = company_name,
        car_name = car_name,
        serialized_device_id=serialized_device_id
    )

def _message_from_db(message_db: Message_DB) -> Message:
    return Message(
        timestamp=message_db.timestamp,
        device_id=DeviceId(
            message_db.module_id,
            message_db.device_type,
            message_db.device_role
        ),
        payload=Payload(
            message_type=message_db.message_type,
            encoding=message_db.payload_encoding,
            data=message_db.payload_data
        )
    )


def _message_db_list(messages: List[Message], message_type: str) -> List[Message_DB]:
    assert(len(messages)>0)
    sdevice_id = serialized_device_id(messages[0].device_id)
    return [
        Message_DB(
            timestamp=message.timestamp,
            serialized_device_id=sdevice_id,
            module_id=message.device_id.module_id,
            device_type=message.device_id.type,
            device_role=message.device_id.role,
            device_name=message.device_id.name,
            message_type=message_type,
            payload_encoding=message.payload.encoding,
            payload_data=message.payload.data # type: ignore
        )
        for message in messages
    ]
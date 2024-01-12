from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any
from enums import MessageType
import re
import logging

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
from database.time import timestamp
from fleetv2_http_api.impl.wait import WaitObjManager

_NAME_PATTERN = "^[0-9a-z_]+$"


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
    """available_cars

    Return list of available cars for all companies registered in the database. # noqa: E501

    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    cars: List[Car] = list()
    device_dict = device_ids()
    for company_name in device_dict:
        for car_name in device_dict[company_name]:
            cars.append(Car(company_name, car_name))
    if cars:
        return _log_and_respond(cars, 200, "Listing available cars.")
    else:
        return _log_and_respond(cars, 200, "No cars were found. Returning empty list.")


def available_devices(
    company_name: str,
    car_name: str,
    module_id: Optional[int] = None
    ) -> Tuple[Module|List[Module], int]:  # noqa: E501

    """available_devices

    Return device Ids for all devices available for contained in the specified car.&lt;br&gt; For a single car module, the device Ids are returned as an object containing module Id and the list of device Ids. &lt;br&gt; If a module Id is specified, only a single such object is returned. &lt;br&gt; Otherwise, a list of such objects is returned, one for each module contained in the car. &lt;br&gt; # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param module_id: An Id of module, an unsigned integer.
    :type module_id: int

    :rtype: Union[AvailableDevices, Tuple[AvailableDevices, int], Tuple[AvailableDevices, int, Dict[str, str]]
    """

    _validate_name_string(company_name, "Company name")
    _validate_name_string(car_name, "Car name")

    company_and_car_name = f"Company='{company_name}', car='{car_name}'"

    device_dict = device_ids()
    if company_name not in device_dict:
        return _log_and_respond([], 404, f"No company named '{company_name}' is registered.")

    elif car_name not in device_dict[company_name]:
        return _log_and_respond([], 404, f"No car named '{car_name}' is registered.")

    if module_id is None:
        car_modules = device_dict[company_name][car_name]
        modules = [_available_module(company_name, car_name, id) for id in car_modules]
        return _log_and_respond(modules, 200, f"Listing available modules ({company_and_car_name})")
    else:
        if module_id not in device_dict[company_name][car_name]:
            return _log_and_respond({}, 404, f"No module with id '{module_id}' is available ({company_and_car_name}).")
        else:
            module = _available_module(company_name, car_name, module_id)
            return _log_and_respond(module, 200, f"Listing available devices in the module '{module_id}' ({company_and_car_name}).")


def list_commands(
    company_name: str,
    car_name: str,
    all_available: Optional[bool] = None,
    since: Optional[int] = None,
    wait: Optional[bool] = None
    ) -> Tuple[List[Message], int]:  # noqa: E501

    """list_commands

    Returns list of the Device Commands. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param all_available: If set, the method returns a complete history of statuses/commands.
    :type all_available: bool
    :param since: A Unix timestamp; if specified, the method returns all messages inclusivelly newer than the specified timestamp \\ (i.e., messages with timestamp greater than or equal to the &#39;since&#39; timestamp)
    :type since: int
    :param wait: An empty parameter. If specified, the method waits for predefined period of time, until some data to be sent in response are available.
    :type wait: bool

    :rtype: Union[List[Message], Tuple[List[Message], int], Tuple[List[Message], int, Dict[str, str]]
    """
    _validate_name_string(company_name, "Company name")
    _validate_name_string(car_name, "Car name")

    company_and_car_name = f"Company='{company_name}', car='{car_name}'"

    db_commands = _list_messages(company_name,car_name,MessageType.COMMAND_TYPE,all_available,since)
    if db_commands or not wait:
        msg, code = _check_car_availability(company_name, car_name)
        if code == 200:
            # device is available and has commands, return them
            cmds = [_message_from_db(m) for m in db_commands]
            return _log_and_respond(cmds, 200, f"Returning commands for available car ({company_and_car_name}).")
        else:
            return _log_and_respond([], 404, f"No commands available at the moment ({company_and_car_name}).")
    else:
        # no commands are available for given device, wait for them
        awaited_commands: List[Message] = _command_wait_manager.wait_and_get_reponse(company_name, car_name)
        if awaited_commands:
            if since is not None and awaited_commands[-1].timestamp < since:
                return _log_and_respond([], 200, f"Found commands, but all are older than 'since' parameter ({company_and_car_name}).")
            return _log_and_respond(awaited_commands, 200, f"Returning awaited commands ({company_and_car_name}).")
        else:
            if company_name not in device_ids() or car_name not in device_ids()[company_name]:
                return _log_and_respond([], 404, f"No commands available before timeout ({company_and_car_name}).")
            return _log_and_respond([], 200, f"Car exists, no command occured before timeout ({company_and_car_name}).")


def list_statuses(
    company_name: str,
    car_name: str,
    all_available: Optional[bool] = None,
    since: Optional[int] = None,
    wait: Optional[bool] = None
    ) -> Tuple[List[Message], int]:  # noqa: E501

    """list_statuses

    It returns list of the Device Statuses. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param all_available: If set, the method returns a complete history of statuses/commands.
    :type all_available: bool
    :param since: A Unix timestamp; if specified, the method returns all messages inclusivelly newer than the specified timestamp \\ (i.e., messages with timestamp greater than or equal to the &#39;since&#39; timestamp)
    :type since: int
    :param wait: An empty parameter. If specified, the method waits for predefined period of time, until some data to be sent in response are available.
    :type wait: bool

    :rtype: Union[List[Message], Tuple[List[Message], int], Tuple[List[Message], int, Dict[str, str]]
    """
    _validate_name_string(company_name, "Company name")
    _validate_name_string(car_name, "Car name")

    company_and_car_name = f"Company='{company_name}', car='{car_name}'"

    db_statuses = _list_messages(company_name, car_name, MessageType.STATUS_TYPE, all_available, since)
    if db_statuses:
        statuses = [_message_from_db(m) for m in db_statuses]
        return _log_and_respond(statuses, 200, f"Returning statuses for available car ({company_and_car_name}).")
    elif not wait:
        return _log_and_respond([], 404, f"No devices (nor their statuses) are available at the moment ({company_and_car_name}).")
    else:
        awaited_statuses: List[Message] = _status_wait_manager.wait_and_get_reponse(company_name, car_name)
        if awaited_statuses:
            if since is not None and awaited_statuses[-1].timestamp < since:
                return _log_and_respond([], 200, f"Found statuses, but all are older than 'since' parameter ({company_and_car_name}).")
            else:
                return _log_and_respond(awaited_statuses, 200, f"Returning awaited statuses ({company_and_car_name}).")
        else:
            return _log_and_respond([], 404, f"No devices (nor their statuses) were available before timeout ({company_and_car_name}).")


def send_commands(
    company_name: str,
    car_name: str,
    body: List[Dict|Message]
    ) -> Tuple[str, int]:  # noqa: E501

    """send_commands

    It adds new device Commands. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param body: Commands to be executed by the device.
    :type body: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    _validate_name_string(company_name, "Company name")
    _validate_name_string(car_name, "Car name")
    messages = _message_list_from_request_body(body)
    if messages == []:
        msg = f"Empty list of commands was sent to the API; no commands were sent to the device."
        return _log_and_respond(msg , 200, msg)
    errors = _check_sent_commands(company_name, car_name, messages)
    if errors[0] != "":
        msg = "; ".join(errors[0].split("\n"))
        return _log_and_respond(errors[0], errors[1], msg)

    _update_messages_timestamp(messages)
    _command_wait_manager.add_response_content_and_stop_waiting(company_name, car_name, messages)
    commands_to_db = _message_db_list(messages, MessageType.COMMAND_TYPE)
    msg, code = send_messages_to_database(company_name, car_name, *commands_to_db)
    return  _log_and_respond(msg, code, msg)


def send_statuses(
    company_name: str,
    car_name: str,
    body: List[Dict|Message]
    ) -> Tuple[str|List[str],int]:  # noqa: E501

    """send_statuses

    Add statuses received from the Device. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param body: Statuses to be send by the device.
    :type body: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    _validate_name_string(company_name, "Company name")
    _validate_name_string(car_name, "Car name")
    messages = _message_list_from_request_body(body)
    if messages == []:
        msg = f"Empty list of statuses was sent to the API; no statuses were sent to the device."
        return _log_and_respond(msg , 200, msg)
    errors = _check_messages(MessageType.STATUS_TYPE, *messages)
    if errors[0] != "":
        msg = "; ".join(errors[0].split("\n"))
        return _log_and_respond(errors[0], errors[1], msg)

    _update_messages_timestamp(messages)
    _status_wait_manager.add_response_content_and_stop_waiting(company_name, car_name, messages)
    response_msg = send_messages_to_database(company_name, car_name, *_message_db_list(messages, MessageType.STATUS_TYPE))
    cmd_warnings = _check_and_handle_first_status(company_name, car_name, messages)
    msg, code = response_msg[0] + cmd_warnings, response_msg[1]
    return  _log_and_respond(msg, code, msg)

def _message_list_from_request_body(body: List[Dict|Message]) -> List[Message]:
    messages: List[Message] = list()
    for item in body:
        if type(item) == dict:
            messages.append(Message.from_dict(item))
        else:
            messages.append(item)
    return messages

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
            message_db.device_role,
            message_db.device_name,
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

def _update_messages_timestamp(messages: Tuple[Message_DB]) -> None:
    timestamp_now = timestamp()
    for message in messages:
        message.timestamp = timestamp_now

def _validate_name_string(name: str, text_label: str) -> None:
    if not re.match(_NAME_PATTERN, name):
        msg = f"{text_label} '{name}' does not match pattern '{_NAME_PATTERN}'."
        raise ValueError(msg)

def _log_and_respond(body: Any, code: int, log_msg: str = "") -> Tuple[Any, int]:
    if log_msg.strip() != "":
        logger = logging.getLogger('werkzeug')
        logger.info(log_msg)
    return body, code  # type: ignore
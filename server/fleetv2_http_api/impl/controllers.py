from __future__ import annotations
from typing import Optional, Any, Iterable, Collection
import logging
import re

from flask import redirect, Response  # type: ignore
from werkzeug import Response as WerkzeugResponse  # type: ignore

from server.enums import MessageType  # type: ignore
from server.fleetv2_http_api.models import Payload, DeviceId, Message, Module, Car  # type: ignore
from server.database.database_controller import (  # type: ignore
    send_messages_to_database,
    Message_DB,
    cleanup_device_commands_and_warn_before_future_commands,
)
from server.database.database_controller import list_messages as _list_messages  # type: ignore
from server.database.connected_cars import (  # type: ignore
    add_car as _add_car,
    add_device as _add_device,
    connected_cars as _connected_cars,
    serialized_device_id as _serialized_device_id,
    is_car_connected as _is_car_connected,
)
from server.database.time import timestamp as _timestamp  # type: ignore
from server.fleetv2_http_api.impl.message_wait import MessageWaitObjManager  # type: ignore
from server.fleetv2_http_api.impl.car_wait import CarWaitObjManager  # type: ignore
from server.fleetv2_http_api.impl.security import SecurityObj  # type: ignore
from server.logs import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


_NAME_PATTERN = "^[0-9a-z_]+$"


_status_wait_manager = MessageWaitObjManager()
_cmd_wait_manager = MessageWaitObjManager()
_car_wait_manager = CarWaitObjManager()
_security = SecurityObj()


def set_status_wait_timeout_s(timeout_s: float) -> None:
    logger.info(f"Setting status wait timeout of Fleet Protocol HTTP API to {timeout_s} s.")
    _status_wait_manager.set_timeout(int(1000 * timeout_s))


def get_status_wait_timeout_s() -> float:
    return _status_wait_manager.timeout_ms * 0.001


def set_command_wait_timeout_s(timeout_s: float) -> None:
    logger.info(f"Setting command wait timeout of Fleet Protocol HTTP API to {timeout_s} s.")
    _cmd_wait_manager.set_timeout(int(1000 * timeout_s))


def get_command_wait_timeout_s() -> float:
    return _cmd_wait_manager.timeout_ms * 0.001


def init_security(
    keycloak_url: str, client_id: str, secret_key: str, scope: str, realm: str, callback: str
) -> None:
    _security.set_config(keycloak_url, client_id, secret_key, scope, realm, callback)


def set_car_wait_timeout_s(timeout_s: float) -> None:
    logger.info(f"Setting car wait timeout of Fleet Protocol HTTP API to {timeout_s} s.")
    _car_wait_manager.set_timeout(int(1000 * timeout_s))


def get_car_wait_timeout_s() -> float:
    return _car_wait_manager.timeout_ms * 0.001


def login(device: Optional[str] = None) -> WerkzeugResponse | Response | tuple[dict | str, int]:
    """login

    Redirect to keycloak login page. If empty device is specified, get authentication url and device code. Try authenticate if device code is provided. # noqa: E501

    :rtype: Response | dict
    """
    if device == "":
        try:
            auth_json = _security.device_get_authentication()
        except:
            msg = "Problem reaching oAuth service."
            return _log_and_respond(msg, 500, msg)
        return _log_and_respond(auth_json, 200, "Device authentication initialized.")
    elif device != None:
        try:
            token = _security.device_token_get(device)  # type: ignore
            return _log_and_respond(token, 200, "Device authenticated, jwt token generated.")
        except:
            msg = "Invalid device code or device still authenticating."
            return _log_and_respond(msg, 400, msg)
    try:
        return redirect(_security.get_authentication_url())
    except:
        msg = "Problem reaching oAuth service."
        return _log_and_respond(msg, 500, msg)


def token_get(
    state: Optional[str] = None,
    session_state: Optional[str] = None,
    iss: Optional[str] = None,
    code: Optional[str] = None,
) -> tuple[dict, int]:
    """token_get

    Get token. Should only be used by keycloak. # noqa: E501

    :param state: State
    :type state: str
    :param session_state: Session state
    :type session_state: str
    :param iss: Code issuer
    :type iss: str
    :param code: Code used to get jwt token
    :type code: str

    :rtype: dict
    """
    try:
        token = _security.token_get(state, session_state, iss, code)  # type: ignore
    except:
        msg = "Problem getting token from oAuth service."
        return _log_and_respond(msg, 500, msg)
    return _log_and_respond(token, 200, "Jwt token generated.")


def token_refresh(refresh_token: str) -> tuple[dict, int]:
    """token_refresh

    Generate a new token using the refresh token. # noqa: E501

    :param refresh_token: Refresh token
    :type refresh_token: str

    :rtype: dict
    """
    try:
        token = _security.token_refresh(refresh_token)
    except:
        msg = "Problem getting token from oAuth service."
        return _log_and_respond(msg, 500, msg)
    return _log_and_respond(token, 200, "Jwt token refreshed.")


def available_cars(wait: bool = False, since: int = 0) -> tuple[list[Car], int]:
    """available_cars

    Return list of available cars for all companies registered in the database. # noqa: E501

    :rtype: Union[list[Car], tuple[list[Car], int], tuple[list[Car], int, dict[str, str]]
    """
    cars: list[Car] = list()
    car_dict = _connected_cars()

    for company_name in car_dict:
        company_cars = [car for car in car_dict[company_name].values() if car.timestamp >= since]
        company_cars.sort(key=lambda x: x.timestamp)
        cars.extend([Car(company_name, car.car_name) for car in company_cars])

    if cars or not wait:
        n = sum([len(car_dict[company_name]) for company_name in car_dict])
        return _log_and_respond(
            cars, 200, f"Found {n} available cars for {len(car_dict)} companies."
        )
    else:
        all_awaited_cars: list[Car] = _car_wait_manager.wait_and_get_reponse()
        awaited_cars = [
            car for car in all_awaited_cars if not _is_car_connected(car.company_name, car.car_name)
        ]
        if awaited_cars:
            n = len(awaited_cars)
            response = _log_and_respond(awaited_cars, 200, f"Returning {n} new available cars.")
            return response
        else:
            return _log_and_respond([], 200, "No cars were found. Returning empty list.")


def available_devices(
    company_name: str, car_name: str, module_id: Optional[int] = None
) -> tuple[Module | list[Module], int]:  # noqa: E501
    """available_devices

    Return device Ids for all devices available for contained in the specified car.&lt;br&gt;

    For a single car module, the device Ids are returned as an object containing module Id
    and the list of device Ids. &lt;br&gt; If a module Id is specified, only a single such
    object is returned. &lt;br&gt; Otherwise, a list of such objects is returned, one for
    each module contained in the car. &lt;br&gt; # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param module_id: An Id of module, an unsigned integer.
    :type module_id: int

    :rtype: Union[AvailableDevices, tuple[AvailableDevices, int],
    tuple[AvailableDevices, int, dict[str, str]]
    """
    company_and_car_name = f"Company='{company_name}', car='{car_name}'"
    empty_response_body: Collection = [] if module_id is None else {}

    cars_dict = _connected_cars()
    if company_name not in cars_dict:
        return _log_and_respond(
            empty_response_body, 404, f"No company named '{company_name}' is registered."
        )

    elif car_name not in cars_dict[company_name]:
        return _log_and_respond(
            empty_response_body, 404, f"No car named '{car_name}' is registered."
        )

    if module_id is None:
        car_modules = cars_dict[company_name][car_name].modules
        modules = [_available_module(company_name, car_name, id) for id in car_modules]
        return _log_and_respond(modules, 200, f"listing available modules ({company_and_car_name})")
    else:
        if module_id not in cars_dict[company_name][car_name].modules:
            return _log_and_respond(
                empty_response_body,
                404,
                f"No module with id '{module_id}' is available ({company_and_car_name}).",
            )
        else:
            module = _available_module(company_name, car_name, module_id)
            return _log_and_respond(
                module,
                200,
                f"listing available devices in the module '{module_id}' ({company_and_car_name}).",
            )


def list_commands(
    company_name: str, car_name: str, since: int = 0, wait: bool = False
) -> tuple[list[Message], int]:  # noqa: E501
    """list_commands

    Returns list of the Device Commands. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param since: A Unix timestamp; if specified, the method returns all messages inclusivelly
    newer than the specified timestamp \\ (i.e., messages with timestamp greater than or equal
    to the &#39;since&#39; timestamp)
    :type since: int
    :param wait: An empty parameter. If specified, the method waits for predefined period of time,
    until some data to be sent in response are available.
    :type wait: bool

    :rtype: Union[list[Message], tuple[list[Message], int], tuple[list[Message], int, dict[str, str]]
    """
    _, code = _car_availability(company_name, car_name)
    car_available = code == 200
    if car_available:
        return _response_for_request_for_connected_cars_commands(
            company_name, car_name, since, wait
        )
    else:
        return _response_for_request_for_disconnected_cars_commands(
            company_name, car_name, since, wait
        )


def list_statuses(
    company_name: str, car_name: str, since: int = 0, wait: bool = False
) -> tuple[list[Message], int]:  # noqa: E501
    """Return list of the device statuses.

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param since: A Unix timestamp; if specified, the method returns all messages inclusivelly
    newer than the specified timestamp \\ (i.e., messages with timestamp greater than or equal
    to the &#39;since&#39; timestamp)
    :type since: int
    :param wait: An empty parameter. If specified, the method waits for predefined period of time,
    until some data to be sent in response are available.
    :type wait: bool
    """
    car = f"Company='{company_name}', car='{car_name}'"
    db_statuses = _list_messages(
        company_name, car_name, (MessageType.STATUS, MessageType.STATUS_ERROR), since
    )
    if db_statuses:
        statuses = [_message_from_db(m) for m in db_statuses]
        return _log_and_respond(statuses, 200, f"Returning statuses for car ({car}).")
    elif not wait:
        if _car_availability(company_name, car_name)[1] == 200:
            return _log_and_respond([], 200, f"No statuses are available ({car}).")
        else:
            return _log_and_respond(
                [], 404, f"Car ({car}) not available. No statuses can be returned."
            )
    else:
        awaited: list[Message] = _status_wait_manager.wait_and_get_reponse(company_name, car_name)
        if awaited:
            if since is not None and awaited[-1].timestamp < since:
                return _log_and_respond(
                    [],
                    200,
                    f"Found only statuses older than 'since' ({car}).",
                )
            else:
                return _log_and_respond(awaited, 200, f"Returning awaited statuses ({car}).")
        else:
            return _log_and_respond([], 404, f"No statuses available before timeout ({car}).")


def send_commands(
    company_name: str, car_name: str, body: list[dict | Message]
) -> tuple[str, int]:  # noqa: E501
    """send_commands

    It adds new device Commands. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param body: Commands to be executed by the device.
    :type body: list | bytes

    :rtype: Union[None, tuple[None, int], tuple[None, int, dict[str, str]]
    """
    messages = _message_list_from_request_body(body)
    if messages == []:
        response = _car_availability(company_name, car_name)
        if response[1] != 200:
            return response
        msg = f"Empty list of commands was sent to the API; no commands were sent to the device."
        return _log_and_respond(msg, 200, msg)
    errors = _check_sent_commands(company_name, car_name, messages)
    if errors[0] != "":
        msg = "; ".join(errors[0].split("\n"))
        return _log_and_respond(errors[0], errors[1], msg)

    _update_messages_timestamp(messages)
    _cmd_wait_manager.add_response_content_and_stop_waiting(company_name, car_name, messages)
    commands_to_db = _message_db_list(messages)
    msg, code = send_messages_to_database(company_name, car_name, *commands_to_db)
    return _log_and_respond(msg, code, msg)


def send_statuses(
    company_name: str, car_name: str, body: list[dict | Message]
) -> tuple[str | list[str], int]:  # noqa: E501
    """send_statuses

    Add statuses received from the Device. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param body: Statuses to be send by the device.
    :type body: list | bytes

    :rtype: Union[None, tuple[None, int], tuple[None, int, dict[str, str]]
    """
    _validate_name_string(company_name, "Company name")
    _validate_name_string(car_name, "Car name")
    messages = _message_list_from_request_body(body)
    if messages == []:
        msg = f"Empty list of statuses was sent to the API; no statuses were sent to the device."
        return _log_and_respond(msg, 200, msg)
    errors = _check_messages((MessageType.STATUS, MessageType.STATUS_ERROR), *messages)
    if errors[0] != "":
        msg = "; ".join(errors[0].split("\n"))
        return _log_and_respond(errors[0], errors[1], msg)

    _update_messages_timestamp(messages)
    _status_wait_manager.add_response_content_and_stop_waiting(company_name, car_name, messages)
    _car_wait_manager.add_response_content_and_stop_waiting([Car(company_name, car_name)])
    response_msg = send_messages_to_database(company_name, car_name, *_message_db_list(messages))
    cmd_warnings = _check_and_handle_first_status(company_name, car_name, messages)
    msg, code = response_msg[0] + cmd_warnings, response_msg[1]
    return _log_and_respond(msg, code, msg)


def _message_list_from_request_body(body: list[dict | Message]) -> list[Message]:
    messages: list[Message] = list()
    for item in body:
        messages.append(Message.from_dict(item) if type(item) == dict else item)
    return messages


def _available_module(company_name: str, car_name: str, module_id: int) -> Module:
    device_id_list = list(
        _connected_cars()[company_name][car_name].modules[module_id].device_ids.values()
    )
    return Module(module_id, device_id_list)


def _check_and_handle_first_status(company: str, car: str, messages: list[Message]) -> str:
    command_removal_warnings = ""
    if not _is_car_connected(company, car):
        response = list_statuses(company, car, wait=False, since=0)
        if response[1] == 200:
            timestamp = min([msg.timestamp for msg in response[0]])
        else:
            timestamp = min([msg.timestamp for msg in messages])
        _add_car(company, car, timestamp)

    for msg in messages:
        device_added = _add_device(company, car, msg.device_id)
        if device_added:
            sdevice_id = _serialized_device_id(msg.device_id)
            command_removal_warnings = "\n".join(
                _handle_first_status_and_return_warnings(msg.timestamp, company, car, sdevice_id)
            )
    if command_removal_warnings.strip() != "":
        command_removal_warnings = "\n\n" + command_removal_warnings
    return command_removal_warnings


def _check_sent_commands(
    company_name: str, car_name: str, messages: list[Message]
) -> tuple[str, int]:
    errors, code = _check_messages(MessageType.COMMAND, *messages)  # type: ignore
    if errors != "" or code != 200:
        return errors, code
    for cmd in messages:
        module_id = cmd.device_id.module_id
        msg, code = _check_device_availability(company_name, car_name, module_id, cmd.device_id)
        if code != 200:
            return msg, code
    return "", 200


def _check_messages(expected_message_types: tuple[str, ...], *messages: Message) -> tuple[str, int]:

    errors: str = ""
    errors = _check_message_types(expected_message_types, *messages)
    if not errors.strip() == "":
        return errors, 400
    else:
        return "", 200


def _check_message_types(expected_message_types: tuple[str, ...], *messages: Message) -> str:
    """Check that type of every message matches the method (send command or send status)."""
    for message in messages:
        if message.payload.message_type not in expected_message_types:
            types = ", ".join(f"{t}" for t in expected_message_types)
            return (
                f"Cannot send a {message.payload.message_type}. "
                f"Expected one of the following message types: {types}"
            )
    return ""


def _check_device_availability(
    company: str, car: str, module_id: int, device_id: DeviceId
) -> tuple[str, int]:
    connected_cars_dict = _connected_cars()
    msg, code = _car_availability(company, car)
    if code != 200:
        return msg, code
    elif module_id not in connected_cars_dict[company][car].modules:
        return (
            f"No module with id '{module_id}' is available in car "
            f"'{car}' under the company '{company}'",
            404,
        )
    elif not connected_cars_dict[company][car].is_connected(device_id):
        return (
            f"No device with id '{_serialized_device_id(device_id)}' is available in module "
            f"'{module_id}' in car '{car}' under the company '{company}'",
            404,
        )
    else:
        return "", 200


def _car_availability(company_name: str, car_name: str) -> tuple[str, int]:
    device_dict = _connected_cars()
    if company_name not in device_dict:
        return f"No car is available under a company '{company_name}'.", 404  # type: ignore
    elif car_name not in device_dict[company_name]:
        return f"Car named '{car_name}' is not available under a company '{company_name}'.", 404
    else:
        return "", 200


def _handle_first_status_and_return_warnings(
    timestamp: int,
    company_name: str,
    car_name: str,
    serialized_device_id: str,
) -> list[str]:

    return cleanup_device_commands_and_warn_before_future_commands(
        current_timestamp=timestamp,
        company_name=company_name,
        car_name=car_name,
        serialized_device_id=serialized_device_id,
    )


def _message_from_db(message_db: Message_DB) -> Message:
    """Convert Message_DB to Message."""
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
            data=message_db.payload_data,
        ),
    )


def _message_db_list(messages: list[Message]) -> list[Message_DB]:
    """Convert list of messages to list of Message_DB."""
    for m in messages:
        if isinstance(m.payload.message_type, MessageType):
            m.payload.message_type = m.payload.message_type.value
    return [
        Message_DB(
            timestamp=message.timestamp,
            serialized_device_id=_serialized_device_id(message.device_id),
            module_id=message.device_id.module_id,
            device_type=message.device_id.type,
            device_role=message.device_id.role,
            device_name=message.device_id.name,
            message_type=message.payload.message_type,
            payload_encoding=message.payload.encoding,
            payload_data=message.payload.data,  # type: ignore
        )
        for message in messages
    ]


def _response_for_request_for_connected_cars_commands(
    company: str, car_name: str, since: int, wait: bool
) -> tuple[list[Message], int]:

    car = f"car '{car_name}' of '{company}'"
    db_commands = _list_messages(company, car_name, (MessageType.COMMAND,), since)
    if db_commands:
        cmds = [_message_from_db(m) for m in db_commands]
        return _log_and_respond(body=cmds, code=200, log_msg=f"Commands for {car}")
    elif wait:
        cmds = _cmd_wait_manager.wait_and_get_reponse(company, car_name)
        if cmds and cmds[-1].timestamp >= since:
            return _log_and_respond(cmds, 200, f"Awaited commands for {car}")
    return _log_and_respond([], 200, f"No commands for {car}.")


def _response_for_request_for_disconnected_cars_commands(
    company: str, car_name: str, since: int, wait: bool
) -> tuple[list[Message], int]:

    if wait:
        cmds = _cmd_wait_manager.wait_and_get_reponse(company, car_name)
        if cmds and cmds[-1].timestamp >= since:
            return _log_and_respond(cmds, 200, f"Awaited commands for '{car_name}' of '{company}'")
    return _log_and_respond(
        [], 404, f"Car '{car_name}' of '{company}' is disconnected. No commands."
    )


def _update_messages_timestamp(messages: Iterable[Message_DB]) -> int:
    timestamp_now = _timestamp()
    for message in messages:
        message.timestamp = timestamp_now
    return timestamp_now


def _log_and_respond(body: Any, code: int, log_msg: str = "") -> tuple[Any, int]:
    if log_msg.strip() != "":
        logger.info(log_msg)
    return body, code  # type: ignore


def _validate_name_string(name: str, text_label: str) -> None:
    if not re.match(_NAME_PATTERN, name):
        msg = f"{text_label} '{name}' does not match pattern '{_NAME_PATTERN}'."
        raise ValueError(msg)

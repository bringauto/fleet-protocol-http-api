import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api import util


def devices_available(module_id=None):  # noqa: E501
    """devices_available

    Returns list of available devices for the whole car or the # noqa: E501

    :param module_id: 
    :type module_id: int

    :rtype: Union[List[Device], Tuple[List[Device], int], Tuple[List[Device], int, Dict[str, str]]
    """
    return 'do some magic!'


def list_commands(device_id, all=None, since=None):  # noqa: E501
    """list_commands

    Returns list of the Device Commands. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: int
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int

    :rtype: Union[List[Payload], Tuple[List[Payload], int], Tuple[List[Payload], int, Dict[str, str]]
    """
    return 'do some magic!'


def list_statuses(device_id, all=None, since=None):  # noqa: E501
    """list_statuses

    It returns list of the Device Statuses. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: int
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int

    :rtype: Union[List[Payload], Tuple[List[Payload], int], Tuple[List[Payload], int, Dict[str, str]]
    """
    return 'do some magic!'


def send_commands(device_id, all=None, since=None, payload=None):  # noqa: E501
    """send_commands

    It adds new device Commands. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: int
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int
    :param payload: Commands to be executed by the device.
    :type payload: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        payload = [Payload.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def send_statuses(device_id, all=None, since=None):  # noqa: E501
    """send_statuses

    Add statuses received from the Device. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: int
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


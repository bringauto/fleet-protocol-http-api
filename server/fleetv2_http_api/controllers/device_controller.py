import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api.models.message import Message  # noqa: E501
from fleetv2_http_api import util


def list_commands(company_name, car_name, sdevice_id, all_available=None, since=None, wait=None):  # noqa: E501
    """list_commands

    Returns list of the Device Commands. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param sdevice_id: The Id of the Device, described with an object.
    :type sdevice_id: str
    :param all_available: If set, the method returns a complete history of statuses/commands.
    :type all_available: str
    :param since: A Unix timestamp; if specified, the method returns all device commands inclusivelly newer than value of specified timestamp.
    :type since: int
    :param wait: An empty parameter. If specified, the method waits for predefined period of time, until some data to be sent in response are available.
    :type wait: str

    :rtype: Union[List[Message], Tuple[List[Message], int], Tuple[List[Message], int, Dict[str, str]]
    """
    return 'do some magic!'


def list_statuses(company_name, car_name, sdevice_id, all_available=None, since=None, wait=None):  # noqa: E501
    """list_statuses

    It returns list of the Device Statuses. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param sdevice_id: The Id of the Device, described with an object.
    :type sdevice_id: str
    :param all_available: If set, the method returns a complete history of statuses/commands.
    :type all_available: str
    :param since: A Unix timestamp; if specified, the method returns all device statuses inclusivelly older than value of specified timestamp.
    :type since: int
    :param wait: An empty parameter. If specified, the method waits for predefined period of time, until some data to be sent in response are available.
    :type wait: str

    :rtype: Union[List[Message], Tuple[List[Message], int], Tuple[List[Message], int, Dict[str, str]]
    """
    return 'do some magic!'


def send_commands(company_name, car_name, sdevice_id, message=None):  # noqa: E501
    """send_commands

    It adds new device Commands. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param sdevice_id: The Id of the Device, described with an object.
    :type sdevice_id: str
    :param message: Commands to be executed by the device.
    :type message: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        message = [Message.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def send_statuses(company_name, car_name, sdevice_id, message=None):  # noqa: E501
    """send_statuses

    Add statuses received from the Device. # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param sdevice_id: The Id of the Device, described with an object.
    :type sdevice_id: str
    :param message: Statuses to be send by the device.
    :type message: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        message = [Message.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'

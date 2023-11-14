import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api.models.device_id import DeviceId  # noqa: E501
from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api import util


def add_device(car_name, company_name, device_id=None):  # noqa: E501
    """add_device

    Add a new device # noqa: E501

    :param car_name: Name of the Car
    :type car_name: str
    :param company_name: Name of the company
    :type company_name: str
    :param device_id: New device
    :type device_id: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        device_id = DeviceId.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def available_devices(car_name, company_name, module_id=None):  # noqa: E501
    """available_devices

    Returns list of available devices for the whole car or a single module. # noqa: E501

    :param car_name: Name of the Car
    :type car_name: str
    :param company_name: Name of the company
    :type company_name: str
    :param module_id: An Id of module.
    :type module_id: dict | bytes

    :rtype: Union[List[DeviceId], Tuple[List[DeviceId], int], Tuple[List[DeviceId], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        module_id =  object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def list_commands(device_id, car_name, company_name, all=None, since=None):  # noqa: E501
    """list_commands

    Returns list of the Device Commands. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: dict | bytes
    :param car_name: Name of the Car
    :type car_name: str
    :param company_name: Name of the company
    :type company_name: str
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int

    :rtype: Union[List[Payload], Tuple[List[Payload], int], Tuple[List[Payload], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        device_id =  DeviceId.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def list_statuses(device_id, car_name, company_name, all=None, since=None):  # noqa: E501
    """list_statuses

    It returns list of the Device Statuses. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: dict | bytes
    :param car_name: Name of the Car
    :type car_name: str
    :param company_name: Name of the company
    :type company_name: str
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int

    :rtype: Union[List[Payload], Tuple[List[Payload], int], Tuple[List[Payload], int, Dict[str, str]]
    """
    if connexion.request.is_json:
        device_id =  DeviceId.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def send_commands(device_id, car_name, company_name, payload=None):  # noqa: E501
    """send_commands

    It adds new device Commands. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: dict | bytes
    :param car_name: Name of the Car
    :type car_name: str
    :param company_name: Name of the company
    :type company_name: str
    :param payload: Commands to be executed by the device.
    :type payload: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        device_id =  DeviceId.from_dict(connexion.request.get_json())  # noqa: E501
    if connexion.request.is_json:
        payload = [Payload.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def send_statuses(device_id, car_name, company_name, payload=None):  # noqa: E501
    """send_statuses

    Add statuses received from the Device. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: dict | bytes
    :param car_name: Name of the Car
    :type car_name: str
    :param company_name: Name of the company
    :type company_name: str
    :param payload: Statuses to be send by the device.
    :type payload: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        device_id =  DeviceId.from_dict(connexion.request.get_json())  # noqa: E501
    if connexion.request.is_json:
        payload = [Payload.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'

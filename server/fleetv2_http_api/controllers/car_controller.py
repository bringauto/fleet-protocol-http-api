import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api.models.car import Car  # noqa: E501
from fleetv2_http_api import util


def add_car(car=None):  # noqa: E501
    """add_car

    Add a new car # noqa: E501

    :param car: New car
    :type car: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        car = Car.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def cars_available():  # noqa: E501
    """cars_available

    It returns the list of available Cars. # noqa: E501


    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    return 'do some magic!'

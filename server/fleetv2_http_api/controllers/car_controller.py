import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api.models.car import Car  # noqa: E501
from fleetv2_http_api import util


def available_cars():  # noqa: E501
    """available_cars

    Return list of available cars for all companies registered in the database. # noqa: E501


    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    return 'do some magic!'

import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from server.fleetv2_http_api.models.car import Car  # noqa: E501
from server.fleetv2_http_api import util


def available_cars(wait=None, since=None):  # noqa: E501
    """available_cars

    Return list of available cars for all companies registered in the database. # noqa: E501

    :param wait: An empty parameter. If specified, the method waits for predefined period of time, until some data to be sent in response are available.
    :type wait: bool
    :param since: A Unix timestamp; if specified, the method returns all messages inclusivelly newer than the specified timestamp \\ (i.e., messages with timestamp greater than or equal to the &#39;since&#39; timestamp)
    :type since: int

    :rtype: Union[List[Car], Tuple[List[Car], int], Tuple[List[Car], int, Dict[str, str]]
    """
    return 'do some magic!'

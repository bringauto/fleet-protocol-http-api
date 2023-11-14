import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api.models.connect_to_database_request import ConnectToDatabaseRequest  # noqa: E501
from fleetv2_http_api import util


def connect_to_database(connect_to_database_request):  # noqa: E501
    """connect_to_database

    Connects to database # noqa: E501

    :param connect_to_database_request: Login data
    :type connect_to_database_request: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        connect_to_database_request = ConnectToDatabaseRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'

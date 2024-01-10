import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api import util


def get_token(state, session_state, iss, code):  # noqa: E501
    """get_token

    Callback endpoint for keycloak to receive jwt token. # noqa: E501

    :param state: State returned by keycloak authentication.
    :type state: str
    :param session_state: Session state returned by keycloak authentication.
    :type session_state: str
    :param iss: Code issuer returned by keycloak authentication.
    :type iss: str
    :param code: Code used for jwt token generation returned by keycloak authentication.
    :type code: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def login():  # noqa: E501
    """login

    Login using keycloak. # noqa: E501


    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'

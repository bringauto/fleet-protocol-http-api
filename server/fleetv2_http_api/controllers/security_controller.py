from typing import Dict, Literal


Role = Literal["visitor", "maintainer"]


KEYS:Dict[Role, str] = {
    "visitor": "visit",
    "maintainer": "maint"
}


def info_from_VisitorAuth(api_key, *args)->Dict:
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """
    
    if api_key == KEYS["visitor"]: 
        return {'client role': "visitor"}
    else: 
        return info_from_MaintainerAuth(api_key, *args)


def info_from_MaintainerAuth(api_key, *args)->Dict:
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """

    if api_key == KEYS["maintainer"]: 
        return {'client role': "maintainer"}
    else: 
        return None # type: ignore

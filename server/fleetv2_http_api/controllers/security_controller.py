from typing import Dict
from database.security import get_client


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
    
    visitor = get_client(api_key, "visitor")
    if visitor == None: 
        return info_from_OperatorAuth(api_key, *args)
    else:
        return {'id': visitor.id,'name': visitor.name}


def info_from_OperatorAuth(api_key, *args)->Dict:
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """

    maintainer = get_client(api_key, "maintainer")
    if maintainer == None: 
        return None # type: ignore
    else:
        return {'id': maintainer.id,'name': maintainer.name}
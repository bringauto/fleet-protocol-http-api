from typing import Dict
from database.security import get_admin


def info_from_AdminAuth(api_key, *args)->Dict:
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """
    admin = get_admin(api_key)
    if admin == None: 
        return None # type: ignore
    else:
        return {'id': admin.id,'name': admin.name}
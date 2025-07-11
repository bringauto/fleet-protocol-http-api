from typing import Dict

import jwt
import connexion as _connexion

from server.database.security import get_admin


_public_key: str
_client_id: str


def set_auth_params(public_key: str, client_id: str) -> None:
    global _public_key
    _public_key = "-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----"
    global _client_id
    _client_id = client_id


def _raise_for_simultaneous_jwt_and_api_key() -> None:
    request = _connexion.request
    api_key_used = "api_key" in request.query_string.decode()
    jwt_used = "Authorization" in request.headers and request.headers["Authorization"].startswith(
        "Bearer "
    )
    if api_key_used and jwt_used:
        raise _connexion.exceptions.AuthenticationProblem(
            status=401,
            detail="Cannot use both API key and JWT token for authentication.",
            title="Authentication error",
        )


def info_from_AdminAuth(api_key, *args) -> Dict:
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """

    _raise_for_simultaneous_jwt_and_api_key()

    admin = get_admin(api_key)
    if admin == None:
        return None  # type: ignore
    else:
        assert admin is not None
        return {"id": admin.id, "name": admin.name}


def info_from_oAuth2AuthCode(token) -> Dict | None:
    """
    Validate and decode token.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.
    'scope' or 'scopes' will be passed to scope validation function.

    :param token Token provided by Authorization header
    :type token: str
    :return: Decoded token information or None if token is invalid
    :rtype: dict | None
    """

    _raise_for_simultaneous_jwt_and_api_key()

    try:
        decoded_token = jwt.decode(token, _public_key, algorithms=["RS256"], audience="account")
    except:
        return None

    for origin in decoded_token["allowed-origins"]:
        if origin == _client_id:
            return {"scopes": {}, "uid": ""}

    return None  # type: ignore


def validate_scope_oAuth2AuthCode(required_scopes, token_scopes):
    """
    Validate required scopes are included in token scope

    :param required_scopes Required scope to access called API
    :type required_scopes: List[str]
    :param token_scopes Scope present in token
    :type token_scopes: List[str]
    :return: True if access to called API is allowed
    :rtype: bool
    """
    # looks for scopes returned by the function above
    # return set(required_scopes).issubset(set(token_scopes))
    return True

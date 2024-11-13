from __future__ import annotations
import abc
from urllib.parse import urlparse

from keycloak import KeycloakOpenID  # type: ignore
import pydantic


class SecurityConfig(pydantic.BaseModel):
    keycloak_url: pydantic.AnyUrl
    client_id: str
    client_secret_key: str
    scope: str
    realm: str


class SecurityObj(abc.ABC):

    @abc.abstractmethod
    def __init__(self, config: SecurityConfig, base_uri: str) -> None:
        pass

    @abc.abstractmethod
    def get_authentication_url(self) -> str:
        pass

    @abc.abstractmethod
    def device_get_authentication(self) -> dict:
        pass

    @abc.abstractmethod
    def token_get(self, state: str, session_state: str, iss: str, code: str) -> dict:
        pass

    @abc.abstractmethod
    def device_token_get(self, device_code: str) -> dict:
        pass

    @abc.abstractmethod
    def token_refresh(self, refresh_token: str) -> dict:
        pass

    def is_not_empty(self) -> bool:
        """Check if the security object is not empty and has all keycloak authentication information."""
        return self is not empty_security_obj


class SecurityObjEmpty(SecurityObj):

    def __init__(self, config: SecurityConfig, base_uri: str) -> None:
        pass

    def get_authentication_url(self) -> str:
        raise self.OAuthAuthenticationNotSet(
            "Cannot get authentication URL. Keycloak authentication is not set"
        )

    def device_get_authentication(self) -> dict:
        raise self.OAuthAuthenticationNotSet(
            "Cannot get device authentication. Keycloak authentication is not set"
        )

    def token_get(self, state: str, session_state: str, iss: str, code: str) -> dict:
        raise self.OAuthAuthenticationNotSet(
            "Cannot get token. Keycloak authentication is not set",
        )

    def device_token_get(self, device_code: str) -> dict:
        raise self.OAuthAuthenticationNotSet(
            "Cannot get device token. Keycloak authentication is not set"
        )

    def token_refresh(self, refresh_token: str) -> dict:
        raise self.OAuthAuthenticationNotSet(
            "Cannot refresh token. Keycloak authentication is not set"
        )

    class OAuthAuthenticationNotSet(Exception):
        pass


empty_security_obj = SecurityObjEmpty(
    SecurityConfig(
        keycloak_url=pydantic.AnyUrl("https://empty"),
        scope="",
        client_id="",
        client_secret_key="",
        realm="",
    ),
    "",
)


class SecurityObjImpl(SecurityObj):
    def __init__(self, config: SecurityConfig, base_uri: str) -> None:
        """Set configuration for keycloak authentication and initialize KeycloakOpenID."""

        self._keycloak_url = config.keycloak_url
        self._scope = config.scope
        self._realm_name = config.realm
        self._callback = base_uri + "/token_get"
        self._state = "state"
        self._oid = KeycloakOpenID(
            server_url=config.keycloak_url,
            client_id=config.client_id,
            realm_name=config.realm,
            client_secret_key=config.client_secret_key,
        )

    def get_authentication_url(self) -> str:
        """Get keycloak url used for authentication."""
        auth_url = self._oid.auth_url(
            redirect_uri=self._callback, scope=self._scope, state=self._state
        )
        return auth_url

    def device_get_authentication(self) -> dict:
        """Get a json for authenticating a device on keycloak."""
        auth_url_device = self._oid.device()
        return auth_url_device

    def token_get(self, state: str, session_state: str, iss: str, code: str) -> dict:
        """Get token from keycloak using a code returned by keycloak."""
        if state != self._state:
            raise Exception("Invalid state")

        if urlparse(iss).geturl() != str(self._keycloak_url) + "/realms/" + self._realm_name:
            raise Exception("Invalid issuer")

        token = self._oid.token(
            grant_type="authorization_code", code=code, redirect_uri=self._callback
        )
        return token

    def device_token_get(self, device_code: str) -> dict:
        """Get token from keycloak using a device code returned by keycloak."""
        token = self._oid.token(
            grant_type="urn:ietf:params:oauth:grant-type:device_code", device_code=device_code
        )
        return token

    def token_refresh(self, refresh_token: str) -> dict:
        """Get a new token from keycloak using the refresh token."""
        token = self._oid.refresh_token(refresh_token=refresh_token)
        return token

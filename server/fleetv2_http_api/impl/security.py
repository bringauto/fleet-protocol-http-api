from __future__ import annotations
import abc
from typing import Protocol
from urllib.parse import urlparse
import uuid

import pydantic


class GetTokenStateMismatch(Exception):
    pass


class GetTokenIssuerMismatch(Exception):
    pass


class KeycloakClient(Protocol):
    """Protocol class for Keycloak OpenID client. Used for type hinting to allow for both
    real implementation using KeycloakOpenID and mock implementation used in tests.
    """

    def auth_url(self, redirect_uri: str, scope: str, state: str) -> str: ...
    def device(self) -> dict: ...
    def token(self, grant_type: str, code: str, redirect_uri: str) -> dict: ...
    def refresh_token(self, refresh_token: str) -> dict: ...


class SecurityConfig(pydantic.BaseModel):
    """Configuration for keycloak authentication."""

    keycloak_url: pydantic.AnyUrl
    client_id: str
    client_secret_key: str
    scope: str
    realm: str


class SecurityObj(abc.ABC):
    """Class for handling keycloak authentication."""

    @classmethod
    def is_defined(cls) -> bool:
        """Check if the security object is defined."""
        return hasattr(cls, "instance")

    @abc.abstractmethod
    def __init__(
        self, config: SecurityConfig, base_uri: str, openid_client: KeycloakClient
    ) -> None:
        pass

    @abc.abstractmethod
    def get_authentication_url(self) -> str:
        pass

    @abc.abstractmethod
    def device_get_authentication(self) -> dict:
        pass

    @abc.abstractmethod
    def token_get(self, state: str, iss: str, code: str) -> dict:
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

    def __init__(self, config: SecurityConfig, base_uri: str, *args, **kwargs) -> None:
        """Empty implementation of SecurityObj. Used when keycloak authentication is not set."""
        pass

    def get_authentication_url(self) -> str:
        raise OAuthAuthenticationNotSet(
            "Cannot get authentication URL. Keycloak authentication is not set. Security object is empty."
        )

    def device_get_authentication(self) -> dict:
        raise OAuthAuthenticationNotSet(
            "Cannot get device authentication. Keycloak authentication is not set.  Security object is empty."
        )

    def token_get(self, state: str, iss: str, code: str) -> dict:
        raise OAuthAuthenticationNotSet(
            "Cannot get token. Keycloak authentication is not set.  Security object is empty.",
        )

    def device_token_get(self, device_code: str) -> dict:
        raise OAuthAuthenticationNotSet(
            "Cannot get device token. Keycloak authentication is not set.  Security object is empty."
        )

    def token_refresh(self, refresh_token: str) -> dict:
        raise OAuthAuthenticationNotSet(
            "Cannot refresh token. Keycloak authentication is not set.  Security object is empty."
        )


class OAuthAuthenticationNotSet(Exception):
    pass


empty_security_obj = SecurityObjEmpty(
    config=SecurityConfig(
        keycloak_url="https://empty",
        scope="",
        client_id="",
        client_secret_key="",
        realm="",
    ),
    base_uri="",
)


class SecurityObjImpl(SecurityObj):

    def __init__(
        self, config: SecurityConfig, base_uri: str, keycloak_client: KeycloakClient
    ) -> None:
        """Set configuration for keycloak authentication and initialize KeycloakOpenID."""

        self._keycloak_url = config.keycloak_url
        self._scope = config.scope
        self._realm_name = config.realm
        self._callback = base_uri + "/token_get"
        self._state = uuid.uuid4().hex
        self._client = keycloak_client

    def get_authentication_url(self) -> str:
        """Get keycloak url used for authentication."""
        auth_url = self._client.auth_url(
            redirect_uri=self._callback, scope=self._scope, state=self._state
        )
        return auth_url

    def device_get_authentication(self) -> dict:
        """Get a json for authenticating a device on keycloak."""
        auth_url_device = self._client.device()
        return auth_url_device

    def token_get(self, state: str, iss: str, code: str) -> dict:
        """Get token from keycloak using a code returned by keycloak."""
        if state != self._state:
            raise GetTokenStateMismatch("Invalid state")

        if self.issuer_url(iss) != self._expected_issuer():
            raise GetTokenIssuerMismatch("Invalid issuer")

        token = self._client.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=self._callback,
        )
        return token

    def device_token_get(self, device_code: str) -> dict:
        """Get token from keycloak using a device code returned by keycloak."""
        token = self._client.token(
            grant_type="urn:ietf:params:oauth:grant-type:device_code",
            code=device_code,
            redirect_uri=self._callback,
        )
        return token

    def token_refresh(self, refresh_token: str) -> dict:
        """Get a new token from keycloak using the refresh token."""
        token = self._client.refresh_token(refresh_token=refresh_token)
        return token

    def _expected_issuer(self) -> str:
        """Get expected issuer URL."""
        return self.issuer_url(str(self._keycloak_url) + "/realms/" + self._realm_name)

    @staticmethod
    def issuer_url(issuer: str) -> str:
        """Parse issuer URL from keycloak configuration."""
        return urlparse(issuer).geturl()

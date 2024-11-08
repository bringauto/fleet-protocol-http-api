from keycloak import KeycloakOpenID  # type: ignore
from urllib.parse import urlparse


class SecurityObj:
    def set_config(
        self,
        keycloak_url: str,
        client_id: str,
        secret_key: str,
        scope: str,
        realm: str,
        base_uri: str,
    ) -> None:
        """Set configuration for keycloak authentication and initialize KeycloakOpenID."""
        self._keycloak_url = keycloak_url
        self._scope = scope
        self._realm_name = realm
        self._callback = base_uri + "/token_get"
        self._state = "state"

        self._oid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm,
            client_secret_key=secret_key,
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

        if urlparse(iss).geturl() != self._keycloak_url + "/realms/" + self._realm_name:
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

from keycloak import KeycloakOpenID
from urllib.parse import urlparse

class SecurityObj:
    def set_config(self, keycloak_url: str, client_id: str, secret_key: str, scope: str, realm: str, callback) -> None:
        self._keycloak_url = keycloak_url
        self._scope = scope
        self._realm_name = realm
        self._callback = callback + "/token_get"
        self._state = "your_state_info"

        self._oid = KeycloakOpenID(
            server_url=keycloak_url,
            client_id=client_id,
            realm_name=realm,
            client_secret_key=secret_key
        )

    def get_authentication_url(self) -> str:
        auth_url = self._oid.auth_url(
            redirect_uri=self._callback,
            scope=self._scope,
            state=self._state
        )
        return auth_url
    
    def token_get(self, state: str, session_state: str, iss: str, code: str) -> dict:
        if state != self._state:
            raise Exception("Invalid state")
        
        if urlparse(iss).geturl() != self._keycloak_url + "/realms/" + self._realm_name:
            raise Exception("Invalid issuer")

        token = self._oid.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=self._callback
        )
        return token
    
    def token_refresh(self, refresh_token: str) -> dict:
        token = self._oid.refresh_token(
            refresh_token=refresh_token
        )
        return token
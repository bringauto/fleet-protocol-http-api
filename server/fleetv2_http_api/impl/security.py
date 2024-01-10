from keycloak import KeycloakOpenID

class SecurityObj:
    def set_config(self, keycloak_url: str, client_id: str, secret_key: str, scope: str, realm: str, callback) -> None:
        self._scope = scope
        self._callback = callback

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
            state="your_state_info"
        )
        return auth_url
    
    def get_token(self, state: str, session_state: str, iss: str, code: str) -> dict:
        token = self._oid.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri=self._callback
        )
        return token
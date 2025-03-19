import unittest
import sys

sys.path.append(".")

from server.fleetv2_http_api.impl.security import (
    SecurityConfig,
    SecurityObjImpl,
    _empty_security_obj,
    UninitializedOAuth,
    GetTokenStateMismatch,
    GetTokenIssuerMismatch,
)
from server.fleetv2_http_api.impl.controllers import (
    init_security_with_client,
    login,
    deinit_security,
)


TEST_TOKEN_HEADER = {"alg": "RS256", "typ": "JWT", "kid": "test"}
TEST_TOKEN_PAYLOAD = {
    "exp": 1000,
    "iat": 1000,
    "auth_time": 1000,
    "jti": "",
    "iss": "",
    "aud": "",
    "sub": "",
    "typ": "Bearer",
    "azp": "",
    "nonce": "",
    "session_state": "",
    "acr": "1",
    "allowed-origins": [],
    "realm_access": {"roles": ["", "offline_access", "uma_authorization"]},
    "resource_access": {
        "account": {"roles": ["manage-account", "manage-account-links", "view-profile"]}
    },
    "scope": "",
    "sid": "",
    "email_verified": False,
    "name": "",
    "preferred_username": "",
    "given_name": "",
    "family_name": "",
    "email": "",
    "group": [],
}
TEST_TOKEN = {"Header": TEST_TOKEN_HEADER, "Payload": TEST_TOKEN_PAYLOAD, "Signature": {}}


class KeycloakClientTest:
    def auth_url(self, redirect_uri: str, scope: str, state: str) -> str:
        return "https://somebasicuri"

    def get_token(self, code: str, redirect_uri: str) -> dict:
        return {}

    def device(self) -> dict:
        return {}

    def token(self, grant_type: str, code: str, redirect_uri: str) -> dict:
        return TEST_TOKEN


class Test_Security_Obj(unittest.TestCase):

    def setUp(self):
        self.client_test = KeycloakClientTest()
        self.config = SecurityConfig(
            keycloak_url="https://empty",
            scope="test",
            client_id="test",
            realm="test",
            client_secret_key="test",
        )

    def test_security_obj_empty_raises_exception(self):
        with self.assertRaises(UninitializedOAuth):
            _empty_security_obj.get_authentication_url()
        with self.assertRaises(UninitializedOAuth):
            _empty_security_obj.device_get_authentication()
        with self.assertRaises(UninitializedOAuth):
            _empty_security_obj.token_get("", "", "")
        with self.assertRaises(UninitializedOAuth):
            _empty_security_obj.device_token_get("")

    def test_authentication_url(self) -> None:
        security_obj = SecurityObjImpl(self.config, "https://somebasicuri", self.client_test)
        self.assertEqual(security_obj.get_authentication_url(), "https://somebasicuri")

    def test_getting_authentication(self) -> None:
        security_obj = SecurityObjImpl(self.config, "https://somebasicuri", self.client_test)
        self.assertEqual(security_obj.device_get_authentication(), {})

    def test_getting_token_without_matching_issuer_raises_exception(self) -> None:
        security_obj = SecurityObjImpl(self.config, "https://somebasicuri", self.client_test)
        with self.assertRaises(GetTokenIssuerMismatch):
            security_obj.token_get(security_obj._state, "", "")

    def test_getting_token_without_matching_state_raises_exception(self) -> None:
        security_obj = SecurityObjImpl(self.config, "https://somebasicuri", self.client_test)
        with self.assertRaises(GetTokenStateMismatch):
            security_obj.token_get("wrong_state", "https://somebasicuri", "")

    def test_getting_token_with_matching_state_and_issuer_returns_token(self) -> None:
        security_obj = SecurityObjImpl(self.config, "https://somebasicuri", self.client_test)
        expected_issuer = str(self.config.keycloak_url) + "/realms/" + str(self.config.realm)
        token = security_obj.token_get(security_obj._state, expected_issuer, "")
        self.assertIsNotNone(token)


class Test_Security_Endpoints(unittest.TestCase):

    def setUp(self):
        self.client_test = KeycloakClientTest()
        self.config = SecurityConfig(
            keycloak_url="https://empty",
            scope="test",
            client_id="test",
            realm="test",
            client_secret_key="test",
        )
        deinit_security()

    def test_calling_login_without_initializing_security_yields_500_error(self):
        response = login()
        self.assertEqual(response[1], 500)

    def test_calling_login_with_device_without_initializing_security_yields_500_error(self):
        response = login("some_device")
        self.assertEqual(response[1], 500)

    def test_calling_login_after_initializing_security_yields_302_code(self):
        init_security_with_client(self.config, "https://somebasicuri", self.client_test)
        response = login()
        self.assertEqual(response.status_code, 302)

    def test_calling_login_after_initializing_security_with_device_yields_302_code(self):
        init_security_with_client(self.config, "https://somebasicuri", self.client_test)
        response = login("some_device")
        self.assertEqual(response[1], 200)


if __name__ == "__main__":  # pragma :no cover
    unittest.main()

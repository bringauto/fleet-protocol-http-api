import unittest
import sys

sys.path.append(".")

from server.fleetv2_http_api.impl.security import SecurityConfig
from server.fleetv2_http_api.impl.controllers import init_security_with_client, login


class KeycloakClientTest:
    def auth_url(self, redirect_uri: str, scope: str, state: str) -> str:
        return "https://somebasicuri"

    def get_token(self, code: str, redirect_uri: str) -> dict:
        return {}


class Test_Setting_Up_Security(unittest.TestCase):

    def setUp(self):
        self.client_test = KeycloakClientTest()

    def test_setting_up_keycloak_security_causes_redirection_to_a_specified_base_uri(self):
        config = SecurityConfig(
            keycloak_url="https://empty",
            scope="test",
            client_id="test",
            client_secret_key="test",
            realm="test",
        )
        init_security_with_client(config, base_uri="https://somebasicuri", client=self.client_test)
        response = login()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "https://somebasicuri")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

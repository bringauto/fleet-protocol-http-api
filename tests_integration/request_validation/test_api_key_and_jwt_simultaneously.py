import unittest

from connexion.exceptions import Unauthorized

from server.app import get_test_app
from tests._utils.logs import clear_logs


class Test_Combining_Security_Schemes(unittest.TestCase):

    def setUp(self):
        clear_logs()
        self.app = get_test_app(base_url="/v2/protocol")

    def test_passing_jwt_token_and_api_key_simultaneously_yields_401_code(self):
        with self.app.app.test_client() as c:
            # Get a JWT token
            # Make a request with both the JWT token and API key
            response = c.get(
                "/cars?api_key=test_key",
                headers={"Authorization": "Bearer f.f.d"},
            )
            print(response.json)
            self.assertEqual(response.status_code, 401)
            self.assertIn("JWT token", response.json["detail"])
            self.assertIn("API key", response.json["detail"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

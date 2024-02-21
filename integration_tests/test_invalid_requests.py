import unittest
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Sending_Status_With_Invalid_Request(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.payload = Payload(
            message_type=MessageType.STATUS_TYPE,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        self.status = Message(device_id=self.device_id, payload=self.payload)

    def test_using_url_with_test_company_name_not_matching_given_pattern(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/status/TestCompany/test_car", json=[self.status])
            self.assertEqual(response.status_code, 400)
        with self.app.app.test_client() as client:
            response = client.post("/status/test_company/TestCar", json=[self.status])
            self.assertEqual(response.status_code, 400)

    def tearDown(self) -> None:
        self.app.clear_all()


if __name__=="__main__":
    unittest.main(verbosity=2)
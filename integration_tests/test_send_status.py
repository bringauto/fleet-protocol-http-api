import unittest
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Making_Car_Available_By_Sending_First_Status(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app()
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.payload = Payload(
            message_type=MessageType.STATUS_TYPE,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        self.status = Message(device_id=self.device_id, payload=self.payload)

    def _test_test_car_is_initially_not_among_available_cars(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get("/v2/protocol/cars")
            self.assertEqual(response.json, [])

    def test_sending_status_makes_car_available(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/v2/protocol/status/test_company/test_car", json=[self.status])
            self.assertEqual(response.status_code, 200)
            response = client.get("/v2/protocol/cars")
            self.assertEqual(response.json, [{"company_name":"test_company", "car_name":"test_car"}])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

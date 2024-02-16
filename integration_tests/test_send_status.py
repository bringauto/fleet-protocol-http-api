import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Making_Car_Available_By_Sending_First_Status(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(db_location="/test_db.db")
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.payload = Payload(
            message_type=MessageType.STATUS_TYPE,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        self.status = Message(device_id=self.device_id, payload=self.payload)
        self.test_car = {"company_name": "test_company", "car_name": "test_car"}

    def test_test_car_is_initially_not_among_available_cars(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get("/v2/protocol/cars")
            self.assertEqual(response.json, [])

    def test_sending_status_makes_car_available(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/v2/protocol/status/test_company/test_car", json=[self.status])
            self.assertEqual(response.status_code, 200)
            response = client.get("/v2/protocol/cars")
            self.assertEqual(response.json, [self.test_car])

    @patch("fleetv2_http_api.impl.controllers.timestamp")
    def test_retrieving_sent_status(self, mock_timestamp: Mock) -> None:
        mock_timestamp.return_value = 11111
        with self.app.app.test_client() as client:
            client.post("/v2/protocol/status/test_company/test_car", json=[self.status])
            response = client.get("/v2/protocol/status/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 11111,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_device",
                            "name": "Test Device",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    }
                ],
            )

    def tearDown(self) -> None:
        self.app.clear_all()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

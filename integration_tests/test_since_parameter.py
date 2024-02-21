import unittest
from unittest.mock import patch, Mock
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Making_Car_Available_By_Sending_First_Status(unittest.TestCase):

    @patch("fleetv2_http_api.impl.controllers.timestamp")
    def setUp(self, mock_timestamp: Mock) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.payload = Payload(MessageType.STATUS_TYPE, "JSON", {"phone": "1234567890"})
        self.status_1 = Message(device_id=self.device_id, payload=self.payload)
        self.status_2 = Message(device_id=self.device_id, payload=self.payload)
        self.status_3 = Message(device_id=self.device_id, payload=self.payload)
        self.status_4 = Message(device_id=self.device_id, payload=self.payload)
        with self.app.app.test_client() as c:
            mock_timestamp.return_value = 10
            c.post("/status/test_company/test_car", json=[self.status_1])
            mock_timestamp.return_value = 20
            c.post("/status/test_company/test_car", json=[self.status_2])
            mock_timestamp.return_value = 30
            c.post("/status/test_company/test_car", json=[self.status_3])
            mock_timestamp.return_value = 40
            c.post("/status/test_company/test_car", json=[self.status_4])

    def test_setting_since_to_zero_returns_all_statuses(self):
        with self.app.app.test_client() as c:
            response = c.get("/status/test_company/test_car?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 4)

    def test_status_older_than_since_timestamp_is_not_returned(self):
        with self.app.app.test_client() as c:
            response = c.get("/status/test_company/test_car?since=15")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["timestamp"], 20)

    def test_status_with_timestamp_equal_to_since_is_returned(self):
        with self.app.app.test_client() as c:
            response = c.get("/status/test_company/test_car?since=20")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["timestamp"], 20)

    def test_setting_since_greater_than_newest_statuses_timestamp_returns_empty_list(self):
        with self.app.app.test_client() as c:
            response = c.get("/status/test_company/test_car?since=50")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def tearDown(self) -> None:
        self.app.clear_all()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

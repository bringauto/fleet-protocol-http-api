import unittest
from unittest.mock import patch, Mock
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType
from server.database.time import timestamp


class Test_Sending_And_Viewing_Command_For_Available_Car(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        status_payload = Payload(
            message_type=MessageType.STATUS,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        self.status = Message(device_id=self.device_id, payload=status_payload)

    @patch("server.database.time.time")
    def test_timestamp_function_returns_milliseconds(self, mocked_time: Mock):
        mocked_time.return_value = 7
        self.assertEqual(timestamp(), 7000)
        mocked_time.return_value = 7.1
        self.assertEqual(timestamp(), 7100)
        mocked_time.return_value = 0
        self.assertEqual(timestamp(), 0)
        mocked_time.return_value = 0.000999
        self.assertEqual(timestamp(), 0)

    def test_status_timestamp_value_in_ms(self):
        with self.app.app.test_client() as client:
            curr_timestamp = timestamp()
            client.post("/status/test_company/test_car", json=[self.status])
            response = client.get("/status/test_company/test_car")
            self.assertTrue(curr_timestamp <= response.json[-1]["timestamp"] < 1000*curr_timestamp)

    def test_command_timestamp_value_in_ms(self):
        command_payload = Payload(
            message_type=MessageType.COMMAND,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        command = Message(device_id=self.device_id, payload=command_payload)
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[self.status])
            curr_timestamp = timestamp()
            client.post("/command/test_company/test_car", json=[command])
            response = client.get("/command/test_company/test_car")
            self.assertGreater(response.json[-1]["timestamp"], curr_timestamp)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

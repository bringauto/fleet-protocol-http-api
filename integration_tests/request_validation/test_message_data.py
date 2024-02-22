import unittest
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Payload, DeviceId
from server.enums import MessageType


class Test_Using_Invalid_Device_ID(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(base_url="/v2/protocol/")
        self.payload = Payload(
            message_type=MessageType.STATUS_TYPE,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        self.invalid_module_ids = [-1, 0.5, "module", None]
        self.invalid_device_types = [-1, 0.5, "type", None]
        self.invalid_device_roles = [
            "testing device",
            "testing-device",
            "TestingDevice",
            "    ",
            "$$$",
            15,
        ]
        self.invalid_device_names = [123, 0.5, None]
        self.payload_json = self.payload.to_dict()

    def test_sending_status_with_invalid_module_id(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_module_id in self.invalid_module_ids:
                with self.subTest(module_id=invalid_module_id):
                    device_id_json = {
                        "module_id": invalid_module_id,
                        "type": 8,
                        "role": "device",
                        "name": "Device",
                    }
                    status_json = {"device_id": device_id_json, "payload": self.payload_json}
                    response = client.post("/status/test_company/test_car", json=[status_json])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("module_id", response.json["detail"])  # type: ignore

    def test_sending_status_with_invalid_device_type(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_type in self.invalid_device_types:
                with self.subTest(device_type=invalid_type):
                    device_id_json = {
                        "module_id": 7,
                        "type": invalid_type,
                        "role": "device",
                        "name": "Device",
                    }
                    status_json = {"device_id": device_id_json, "payload": self.payload_json}
                    response = client.post("/status/test_company/test_car", json=[status_json])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("type", response.json["detail"])  # type: ignore

    def test_sending_status_with_invalid_device_role(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_role in self.invalid_device_roles:
                with self.subTest(device_role=invalid_role):
                    device_id_json = {
                        "module_id": 7,
                        "type": 8,
                        "role": invalid_role,
                        "name": "Device",
                    }
                    status_json = {"device_id": device_id_json, "payload": self.payload_json}
                    response = client.post("/status/test_company/test_car", json=[status_json])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("role", response.json["detail"])  # type: ignore

    def test_sending_status_with_invalid_device_name(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_name in self.invalid_device_names:
                with self.subTest(device_name=invalid_name):
                    device_id_json = {
                        "module_id": 7,
                        "type": 8,
                        "role": "device",
                        "name": invalid_name,
                    }
                    status_json = {"device_id": device_id_json, "payload": self.payload_json}
                    response = client.post("/status/test_company/test_car", json=[status_json])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("name", response.json["detail"])  # type: ignore

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Invalid_Message_Payload_Yields_Code_400(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.invalid_message_types = ["status", 0, None, "unknown type"]
        self.invalid_encodings = ["json", 0, None, "unknown encoding"]
        self.invalid_data = [123, 0.5, None]

    def test_sending_status_with_invalid_message_type(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_message_type in self.invalid_message_types:
                with self.subTest(message_type=invalid_message_type):
                    payload_json = {
                        "message_type": invalid_message_type,
                        "encoding": "JSON",
                        "data": {"phone_number": "1234567890"},
                    }
                    status_json = {"device_id": self.device_id.to_dict(), "payload": payload_json}
                    response = client.post("/status/test_company/test_car", json=[status_json])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("message_type", response.json["detail"])  # type: ignore

    def test_sending_status_with_invalid_encoding(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_encoding in self.invalid_encodings:
                with self.subTest(encoding=invalid_encoding):
                    payload_json = {
                        "message_type": "STATUS",
                        "encoding": invalid_encoding,
                        "data": {"phone_number": "1234567890"},
                    }
                    status_json = {"device_id": self.device_id.to_dict(), "payload": payload_json}
                    response = client.post("/status/test_company/test_car", json=[status_json])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("encoding", response.json["detail"])  # type: ignore

    def test_sending_status_with_invalid_data(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_data in self.invalid_data:
                with self.subTest(data=invalid_data):
                    payload_json = {
                        "message_type": "STATUS",
                        "encoding": "JSON",
                        "data": invalid_data,
                    }
                    status_json = {"device_id": self.device_id.to_dict(), "payload": payload_json}
                    response = client.post("/status/test_company/test_car", json=[status_json])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("data", response.json["detail"])  # type: ignore


if __name__ == "__main__":
    unittest.main(verbosity=2, buffer=True)

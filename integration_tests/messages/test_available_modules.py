import unittest
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Listing_Available_Devices_Without_Filtering_By_Module(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = 1000
        self.app = _app.get_test_app(base_url="/v2/protocol/")
        self.device_1_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device 1")
        self.device_2_id = DeviceId(module_id=9, type=5, role="test_device", name="Test Device 2")
        status_payload = Payload(MessageType.STATUS_TYPE, "JSON", {"phone": "1234567890"})
        self.status_1 = Message(device_id=self.device_1_id, payload=status_payload)
        self.status_2 = Message(device_id=self.device_2_id, payload=status_payload)

    def test_404_and_empty_list_of_devices_is_returned_if_no_statuses_are_sent(self):
        with self.app.app.test_client() as client:
            response = client.get("/available-devices/test_company/test_car")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, [])

    def test_404_and_empty_list_of_devices_are_returned_for_other_car_than_status_was_sent_to(self):
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[self.status_1, self.status_2])
            response = client.get("/available-devices/test_company/test_car_2")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, [])

            response = client.get("/available-devices/test_company/test_car")
            self.assertEqual(response.status_code, 200)

    def test_listing_available_devices_without_filtering_by_module(self) -> None:
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[self.status_1, self.status_2])
            response = client.get("/available-devices/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                [
                    {
                        "device_list": [
                            {
                                "module_id": 7,
                                "type": 8,
                                "role": "test_device",
                                "name": "Test Device 1",
                            }
                        ],
                        "module_id": 7,
                    },
                    {
                        "device_list": [
                            {
                                "module_id": 9,
                                "type": 5,
                                "role": "test_device",
                                "name": "Test Device 2",
                            }
                        ],
                        "module_id": 9,
                    },
                ],
            )

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Filtering_Available_Devices_By_Module(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = 1000
        self.app = _app.get_test_app(base_url="/v2/protocol/")
        self.device_1_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device 1")
        self.device_2_id = DeviceId(module_id=9, type=5, role="test_device", name="Test Device 2")
        status_payload = Payload(MessageType.STATUS_TYPE, "JSON", {"phone": "1234567890"})
        self.status_1 = Message(device_id=self.device_1_id, payload=status_payload)
        self.status_2 = Message(device_id=self.device_2_id, payload=status_payload)

    def test_404_and_empty_list_is_returned_if_no_statuses_are_sent(self):
        with self.app.app.test_client() as client:
            response = client.get("/available-devices/test_company/test_car?module_id=10")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {})

    def test_404_and_empty_json_is_returned_for_other_module_than_status_was_sent_to(self):
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[self.status_1, self.status_2])
            response = client.get("/available-devices/test_company/test_car?module_id=10")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {})

    def test_filtering_devices_by_module(self) -> None:
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[self.status_1, self.status_2])
            response = client.get("/available-devices/test_company/test_car?module_id=7")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                {
                    "device_list": [
                        {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_device",
                            "name": "Test Device 1",
                        }
                    ],
                    "module_id": 7,
                },
            )
            response = client.get("/available-devices/test_company/test_car?module_id=9")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                {
                    "device_list": [
                        {
                            "module_id": 9,
                            "type": 5,
                            "role": "test_device",
                            "name": "Test Device 2",
                        }
                    ],
                    "module_id": 9,
                },
            )

    def tearDown(self) -> None:
        self.app.clear_all()


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2, buffer=True)

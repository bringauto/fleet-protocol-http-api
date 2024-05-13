import unittest
from unittest.mock import patch, Mock
import time
from concurrent.futures import ThreadPoolExecutor as _Executor
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Filtering_Sent_Statuses_By_Since_Parameter(unittest.TestCase):
    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def setUp(self, mock_timestamp: Mock) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
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

    def test_setting_since_greater_than_newest_statuses_timestamp_returns_empty_list_and_code_200(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get("/status/test_company/test_car?since=50")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Filtering_Sent_Commands_By_Since_Parameter(unittest.TestCase):
    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def setUp(self, mock_timestamp: Mock) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.status_payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
        status = Message(device_id=self.device_id, payload=self.status_payload)
        payload_1 = Payload(MessageType.COMMAND, "JSON", {"command": "1"})
        payload_2 = Payload(MessageType.COMMAND, "JSON", {"command": "2"})
        payload_3 = Payload(MessageType.COMMAND, "JSON", {"command": "3"})
        payload_4 = Payload(MessageType.COMMAND, "JSON", {"command": "4"})
        self.command_1 = Message(device_id=self.device_id, payload=payload_1)
        self.command_2 = Message(device_id=self.device_id, payload=payload_2)
        self.command_3 = Message(device_id=self.device_id, payload=payload_3)
        self.command_4 = Message(device_id=self.device_id, payload=payload_4)

        with self.app.app.test_client() as c:
            mock_timestamp.return_value = 10
            c.post("/status/test_company/test_car", json=[status])
            mock_timestamp.return_value = 20
            c.post("/command/test_company/test_car", json=[self.command_1])
            mock_timestamp.return_value = 30
            c.post("/command/test_company/test_car", json=[self.command_2])
            mock_timestamp.return_value = 40
            c.post("/command/test_company/test_car", json=[self.command_3])
            mock_timestamp.return_value = 50
            c.post("/command/test_company/test_car", json=[self.command_4])

    def test_setting_since_to_zero_returns_all_commands(self):
        with self.app.app.test_client() as c:
            response = c.get("/command/test_company/test_car?since=0")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 4)
            self.assertEqual(response.json[0]["payload"]["data"]["command"], "1")

    def test_command_older_than_since_timestamp_is_not_returned(self):
        with self.app.app.test_client() as c:
            response = c.get("/command/test_company/test_car?since=25")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["payload"]["data"]["command"], "2")

    def test_command_with_timestamp_equal_to_since_is_returned(self):
        with self.app.app.test_client() as c:
            response = c.get("/command/test_company/test_car?since=30")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 3)
            self.assertEqual(response.json[0]["payload"]["data"]["command"], "2")

    def test_setting_since_greater_than_newest_commands_timestamp_returns_empty_list_and_code_200(
        self,
    ):
        with self.app.app.test_client() as c:
            response = c.get("/command/test_company/test_car?since=60")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Setting_Wait_To_True_When_All_Statuses_Are_Filtered_Out_By_Since_Parameter(
    unittest.TestCase
):
    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def setUp(self, mock_timestamp: Mock) -> None:
        self.app = _app.get_test_app(
            db_location="test_db.db", base_url="/v2/protocol/", request_timeout_s=0.2
        )
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
        self.status_1 = Message(device_id=self.device_id, payload=self.payload)
        self.status_2 = Message(device_id=self.device_id, payload=self.payload)
        self.status_3 = Message(device_id=self.device_id, payload=self.payload)
        self.status_4 = Message(device_id=self.device_id, payload=self.payload)
        self.status_5 = Message(device_id=self.device_id, payload=self.payload)
        with self.app.app.test_client() as c:
            mock_timestamp.return_value = 10
            c.post("/status/test_company/test_car", json=[self.status_1])
            mock_timestamp.return_value = 20
            c.post("/status/test_company/test_car", json=[self.status_2])
            mock_timestamp.return_value = 30
            c.post("/status/test_company/test_car", json=[self.status_3])
            mock_timestamp.return_value = 40
            c.post("/status/test_company/test_car", json=[self.status_4])

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_thread_waits_for_status_with_newer_timestamp_than_since_parameter(
        self, mock_timestamp: Mock
    ):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/status/test_company/test_car?since=50&wait=True")
            mock_timestamp.return_value = 60
            time.sleep(0.01)
            executor.submit(c.post, "/status/test_company/test_car", json=[self.status_5])
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]["timestamp"], 60)  # type: ignore

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_status_with_timestamp_older_than_since_parameter_will_not_resume_waiting_thread(
        self, mock_timestamp: Mock
    ):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/status/test_company/test_car?since=100&wait=True")
            mock_timestamp.return_value = 80
            time.sleep(0.01)
            executor.submit(c.post, "/status/test_company/test_car", json=[self.status_5])
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Setting_Wait_To_True_When_All_Commands_Are_Filtered_Out_By_Since_Parameter(
    unittest.TestCase
):
    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def setUp(self, mock_timestamp: Mock) -> None:
        self.app = _app.get_test_app(
            db_location="test_db.db", base_url="/v2/protocol/", request_timeout_s=0.2
        )
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        status_payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
        status = Message(device_id=self.device_id, payload=status_payload)

        self.payload_1 = Payload(MessageType.COMMAND, "JSON", {"command": "1"})
        self.payload_2 = Payload(MessageType.COMMAND, "JSON", {"command": "2"})
        self.payload_3 = Payload(MessageType.COMMAND, "JSON", {"command": "3"})
        self.payload_4 = Payload(MessageType.COMMAND, "JSON", {"command": "4"})

        self.command_1 = Message(device_id=self.device_id, payload=self.payload_1)
        self.command_2 = Message(device_id=self.device_id, payload=self.payload_2)
        self.command_3 = Message(device_id=self.device_id, payload=self.payload_3)
        self.command_4 = Message(device_id=self.device_id, payload=self.payload_4)

        with self.app.app.test_client() as c:
            mock_timestamp.return_value = 10
            c.post("/status/test_company/test_car", json=[status])
            mock_timestamp.return_value = 20
            c.post("/command/test_company/test_car", json=[self.command_1])
            mock_timestamp.return_value = 30
            c.post("/command/test_company/test_car", json=[self.command_2])
            mock_timestamp.return_value = 40
            c.post("/command/test_company/test_car", json=[self.command_3])

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_thread_waits_for_command_with_newer_timestamp_than_since_parameter(
        self, mock_timestamp: Mock
    ):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/command/test_company/test_car?since=50&wait=True")
            mock_timestamp.return_value = 55
            time.sleep(0.01)
            executor.submit(c.post, "/command/test_company/test_car", json=[self.command_4])
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]["timestamp"], 55)  # type: ignore

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_command_with_timestamp_older_than_since_parameter_will_not_resume_waiting_thread(
        self, mock_timestamp: Mock
    ):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/command/test_company/test_car?since=100&wait=True")
            mock_timestamp.return_value = 80
            time.sleep(0.01)
            executor.submit(c.post, "/command/test_company/test_car", json=[self.command_4])
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def tearDown(self) -> None:
        self.app.clear_all()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

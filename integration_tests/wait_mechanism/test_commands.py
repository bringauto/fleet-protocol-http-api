import unittest
import sys
from concurrent.futures import ThreadPoolExecutor as _Executor
import time
import os

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Waiting_For_Commands_For_Already_Available_Car(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(
            db_location="test_db.db", request_timeout_s=0.2, base_url="/v2/protocol/"
        )
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        status_payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
        self.command_payload = Payload(MessageType.COMMAND, "JSON", {"instruction": "start"})
        self.command = Message(device_id=self.device_id, payload=self.command_payload)
        status = Message(device_id=self.device_id, payload=status_payload)
        with self.app.app.test_client() as c:
            c.post("status/test_company/test_car", json=[status])

    def test_if_status_and_relevant_command_is_sent_before_timeout_code_200_and_empty_list_are_returned(
        self,
    ):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            time.sleep(0.05)
            future = executor.submit(c.get, "/command/test_company/test_car?wait=True")
            time.sleep(0.05)
            executor.submit(c.post, "/command/test_company/test_car", json=[self.command])
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json[0]["payload"]["data"]["instruction"], "start")

    def test_if_status_but_no_command_is_sent_before_timeout_code_200_and_empty_list_are_returned(
        self,
    ):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/command/test_company/test_car?wait=True")
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

    def test_if_no_relevant_status_is_sent_before_timeout_code_404_and_empty_list_are_returned(
        self,
    ):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/command/other_company/other_car?wait=True")
            response = future.result()
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, [])

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")
        self.app.clear_all()


class Test_Waiting_For_Commands_Of_Initially_Unavailable_Car(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(
            db_location="test_db.db", request_timeout_s=0.2, base_url="/v2/protocol/"
        )
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.status_payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
        self.command_1_payload = Payload(MessageType.COMMAND, "JSON", {"instruction": "start"})
        self.command_2_payload = Payload(MessageType.COMMAND, "JSON", {"instruction": "stop"})
        self.command_1 = Message(device_id=self.device_id, payload=self.command_1_payload)
        self.command_2 = Message(device_id=self.device_id, payload=self.command_2_payload)
        self.status = Message(device_id=self.device_id, payload=self.status_payload)

    def test_no_status_being_sent_before_timeout_yields_code_404_and_empty_list(self):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/command/test_company/test_car?wait=True")
            response = future.result()
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, [])

    def test_commands_sent_before_car_becomes_available_are_not_sent_to_waiting_thread(self):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/command/test_company/test_car?wait=True")
            time.sleep(0.05)
            # this command will be ignored by the waiting thread
            executor.submit(c.post, "/command/test_company/test_car", json=[self.command_1])
            executor.submit(c.post, "/status/test_company/test_car", json=[self.status])
            time.sleep(0.05)
            executor.submit(c.post, "/command/test_company/test_car", json=[self.command_2])
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["payload"]["data"]["instruction"], "stop")

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")
        self.app.clear_all()


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2, buffer=True)

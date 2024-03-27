import unittest
import sys
from concurrent.futures import ThreadPoolExecutor as _Executor
import time
import os

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Waiting_For_Statuses_To_Become_Available(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(
            db_location="test_db.db", request_timeout_s=0.2, base_url="/v2/protocol/"
        )
        self.deviceA_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.deviceB_id = DeviceId(module_id=9, type=10, role="test_device", name="Test Device")
        self.payload = Payload(MessageType.STATUS_TYPE, "JSON", {"phone": "1234567890"})
        self.statusA = Message(device_id=self.deviceA_id, payload=self.payload)
        self.statusB = Message(device_id=self.deviceB_id, payload=self.payload)

    def test_awaited_statuses_are_returned_if_some_status_is_sent_in_other_thread(self):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/status/test_company/test_car?wait=True")
            time.sleep(0.1)
            executor.submit(c.post, "/status/test_company/test_car", json=[self.statusA])
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["device_id"], self.deviceA_id.to_dict())

    def test_all_relevant_statuses_sent_in_one_thread_are_returned_in_second_waiting_thread(self):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/status/test_company/test_car?wait=True")
            time.sleep(0.1)
            executor.submit(
                c.post,
                "/status/test_company/test_car",
                json=[self.statusA, self.statusB],
            )
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["device_id"], self.deviceA_id.to_dict())
            self.assertEqual(response.json[1]["device_id"], self.deviceB_id.to_dict())

    def test_404_code_and_empty_list_of_statuses_is_returned_after_timeout_is_exceeded(self):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/status/test_company/test_car?wait=True")
            response = future.result()
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, [])

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Waiting_Request_Ignores_Statuses_Send_To_Other_Cars(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(
            db_location="test_db.db", request_timeout_s=0.2, base_url="/v2/protocol/"
        )
        self.deviceA_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.deviceB_id = DeviceId(module_id=9, type=10, role="test_device", name="Test Device")
        self.payload = Payload(MessageType.STATUS_TYPE, "JSON", {"phone": "1234567890"})
        self.statusA = Message(device_id=self.deviceA_id, payload=self.payload)
        self.statusB = Message(device_id=self.deviceB_id, payload=self.payload)

    def test_status_for_other_car_than_awaited_is_not_send_to_waiting_thread(self):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/status/company/car_x?wait=True")
            time.sleep(0.1)
            executor.submit(c.post, "/status/company/car_y", json=[self.statusA, self.statusB])
            response = future.result()
            self.assertEqual(response.status_code, 404)
            self.assertEqual(len(response.json), 0)

    def test_status_for_other_company_than_awaited_is_not_send_to_waiting_thread(self):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/status/company_x/car?wait=True")
            time.sleep(0.1)
            executor.submit(c.post, "/status/company_y/car", json=[self.statusA, self.statusB])
            response = future.result()
            self.assertEqual(response.status_code, 404)
            self.assertEqual(len(response.json), 0)

    def test_waiting_thread_responds_after_relevant_status_is_sent(self):
        with _Executor(max_workers=2) as executor, self.app.app.test_client() as c:
            future = executor.submit(c.get, "/status/company/car?wait=True")
            time.sleep(0.05)
            # This status does not trigger response from the waiting thread
            executor.submit(c.post, "/status/company/some_other_car", json=[self.statusA])
            time.sleep(0.05)
            # This status triggers response from the waiting thread
            executor.submit(c.post, "/status/company/car", json=[self.statusB])
            response = future.result()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 1)
            self.assertEqual(response.json[0]["device_id"], self.deviceB_id.to_dict())

    def tearDown(self) -> None:
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

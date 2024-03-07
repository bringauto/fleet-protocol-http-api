import unittest
import sys
import os
import time

sys.path.append("server")

from fleetv2_http_api.models import Payload, Message, Car, DeviceId  # type: ignore
from enums import MessageType, EncodingType  # type: ignore
from database.database_controller import set_test_db_connection, clear_device_ids  # type: ignore
from fleetv2_http_api.impl.controllers import (  # type: ignore
    available_cars, send_statuses, set_car_wait_timeout_s
)
from _misc import run_in_threads  # type: ignore


class Test_Waiting_For_Available_Cars(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")
        set_test_db_connection("/example.db")
        clear_device_ids()
        self.status_1 = Message(
            device_id=DeviceId(module_id=47, type=5, role="test_device", name="Test Device"),
            payload=Payload(
                message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={}
            ),
        )

    def test_if_cars_are_available_no_waiting_applies(self):
        send_statuses(company_name="company", car_name="car", body=[self.status_1])
        cars = available_cars(wait=True)
        self.assertListEqual(cars[0], [Car(company_name="company", car_name="car")])

    def test_waiting_for_single_car_to_become_available(self):
        def send_single_status():
            time.sleep(0.1)
            send_statuses("test_company", "test_car", [self.status_1])
        def list_cars():
            cars = available_cars(wait=True)[0]
            self.assertEqual(cars, [Car(company_name="test_company", car_name="test_car")])
        run_in_threads(send_single_status, list_cars)

    def test_exceeding_timeout_waiting_for_available_cars_yields_an_empty_list(self):
        set_car_wait_timeout_s(0.1)
        cars, code = available_cars(wait=True)
        self.assertEqual(cars, [])
        self.assertEqual(code, 200)

    def tearDown(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")


if __name__ == "__main__":
    unittest.main()

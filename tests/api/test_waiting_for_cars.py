import unittest
import sys
import os
import time
from unittest.mock import patch, Mock
sys.path.append(".")

from server.fleetv2_http_api.models import Payload, Message, Car, DeviceId  # type: ignore
from server.enums import MessageType, EncodingType  # type: ignore
from server.database.database_controller import (  # type: ignore
    set_test_db_connection,
    clear_connected_cars,
    connected_cars,
)
from server.fleetv2_http_api.impl.controllers import (  # type: ignore
    available_cars,
    send_statuses,
    set_car_wait_timeout_s,
)
from tests.api.misc import run_in_threads  # type: ignore
from server.logs import clear_logs  # type: ignore


class Test_Waiting_For_Available_Cars(unittest.TestCase):
    def setUp(self) -> None:
        clear_logs()
        if os.path.exists("./example.db"):
            os.remove("./example.db")
        set_test_db_connection("/example.db")
        clear_connected_cars()
        self.status_1 = Message(
            device_id=DeviceId(module_id=47, type=5, role="test_device", name="Test Device"),
            payload=Payload(message_type=MessageType.STATUS, encoding=EncodingType.JSON, data={}),
        )

    def test_if_cars_are_available_no_waiting_applies(self):
        send_statuses(company_name="company", car_name="car", body=[self.status_1])
        cars = available_cars(wait=True)
        self.assertListEqual(cars[0], [Car(company_name="company", car_name="car")])

    def test_waiting_for_single_car_to_become_available(self):
        set_car_wait_timeout_s(1)

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

    def test_multiple_requests_for_cars(self):
        set_car_wait_timeout_s(1)

        def list_cars_1():
            cmds, code = available_cars(wait=True)
            self.assertEqual(len(cmds), 1, "First response contains the command.")

        def list_cars_2():
            cmds, code = available_cars(wait=True)
            self.assertEqual(len(cmds), 1, "Second response contains the command.")

        def send_test_status():
            time.sleep(0.5)
            send_statuses("test_company", "test_car", [self.status_1])

        run_in_threads(list_cars_1, list_cars_2, send_test_status)

    def tearDown(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")


class Test_Storing_Car_Connection_Time(unittest.TestCase):

    def setUp(self) -> None:
        clear_logs()
        if os.path.exists("./example.db"):
            os.remove("./example.db")
        set_test_db_connection("/example.db")
        clear_connected_cars()
        self.status = Message(
            device_id=DeviceId(module_id=47, type=5, role="test_device", name="Test Device"),
            payload=Payload(message_type=MessageType.STATUS, encoding=EncodingType.JSON, data={}),
        )
        self.status_error = Message(
            device_id=DeviceId(module_id=47, type=5, role="test_device", name="Test Device"),
            payload=Payload(
                message_type=MessageType.STATUS_ERROR, encoding=EncodingType.JSON, data={}
            ),
        )

    @patch("server.database.time._time_in_ms")
    def test_connection_time_is_taken_from_first_status_and_stored_with_the_car(
        self, mocked_time_in_ms: Mock
    ):
        mocked_time_in_ms.return_value = 1000
        send_statuses("test_company", "test_car", [self.status])
        self.assertEqual(connected_cars()["test_company"]["test_car"].timestamp, 1000)

    @patch("server.database.time._time_in_ms")
    def test_connection_time_is_taken_from_the_first_status_error_stored_with_the_car_(
        self, mocked_time_in_ms: Mock
    ):
        mocked_time_in_ms.return_value = 1000
        send_statuses("test_company", "test_car", [self.status_error])
        self.assertEqual(connected_cars()["test_company"]["test_car"].timestamp, 1000)

    @patch("server.database.time._time_in_ms")
    def test_connection_time_is_preserved_when_sending_another_status(
        self, mocked_time_in_ms: Mock
    ):
        mocked_time_in_ms.return_value = 1000
        send_statuses("test_company", "test_car", [self.status])
        mocked_time_in_ms.return_value = 2000
        send_statuses("test_company", "test_car", [self.status])
        self.assertEqual(connected_cars()["test_company"]["test_car"].timestamp, 1000)
        mocked_time_in_ms.return_value = 3000
        send_statuses("test_company", "test_car", [self.status_error])
        self.assertEqual(connected_cars()["test_company"]["test_car"].timestamp, 1000)

    @patch("server.database.time._time_in_ms")
    def test_connection_time_is_not_updated_after_clearing_up_the_connected_cars(
        self, mocked_time_in_ms: Mock
    ):
        mocked_time_in_ms.return_value = 1000
        send_statuses("test_company", "test_car", [self.status])
        mocked_time_in_ms.return_value = 2000
        send_statuses("test_company", "test_car", [self.status])
        clear_connected_cars()
        mocked_time_in_ms.return_value = 3000
        send_statuses("test_company", "test_car", [self.status])
        self.assertEqual(connected_cars()["test_company"]["test_car"].timestamp, 1000)

    def tearDown(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")


class Test_Filtering_Connected_Car_By_Connection_Time_With_Since_Parameter(unittest.TestCase):

    def setUp(self) -> None:
        clear_logs()
        if os.path.exists("./example.db"):
            os.remove("./example.db")
        set_test_db_connection("/example.db")
        clear_connected_cars()
        self.status = Message(
            device_id=DeviceId(module_id=47, type=5, role="test_device", name="Test Device"),
            payload=Payload(message_type=MessageType.STATUS, encoding=EncodingType.JSON, data={}),
        )
        self.status_error = Message(
            device_id=DeviceId(module_id=47, type=5, role="test_device", name="Test Device"),
            payload=Payload(
                message_type=MessageType.STATUS_ERROR, encoding=EncodingType.JSON, data={}
            ),
        )

    @patch("server.database.time._time_in_ms")
    def test_since_set_to_zero_returns_all_connected_cars(self, mocked_time_in_ms: Mock):
        mocked_time_in_ms.return_value = 0
        send_statuses("test_company", "test_car", [self.status])
        cars, code = available_cars(wait=True, since=0)
        self.assertEqual(len(cars), 1)

    @patch("server.database.time._time_in_ms")
    def test_since_set_to_positive_value_returns_all_cars_connected_at_the_time_or_later(
        self, mocked_time_in_ms: Mock
    ):
        mocked_time_in_ms.return_value = 1000
        send_statuses("test_company", "car_1", [self.status])
        mocked_time_in_ms.return_value = 2000
        send_statuses("test_company", "car_2", [self.status])
        mocked_time_in_ms.return_value = 3000
        send_statuses("test_company", "car_3", [self.status_error])
        mocked_time_in_ms.return_value = 4000
        send_statuses("test_company", "car_4", [self.status])
        cars, code = available_cars(since=2500)
        self.assertEqual(len(cars), 2)
        self.assertEqual(cars[0].car_name, "car_3")
        self.assertEqual(cars[1].car_name, "car_4")

    @patch("server.database.time._time_in_ms")
    def test_request_timeout_for_when_only_old_car_is_connected(self, mocked_time_in_ms: Mock):
        set_car_wait_timeout_s(0.2)
        mocked_time_in_ms.return_value = 1000
        send_statuses("test_company", "car_1", [self.status])
        cars, code = available_cars(wait=True, since=4500)
        self.assertEqual(len(cars), 0)

    @patch("server.database.time._time_in_ms")
    def test_request_timeout_for_when_old_car_is_connected_with_repeatedly_sent_status(
        self, mocked_time_in_ms: Mock
    ):
        set_car_wait_timeout_s(0.5)
        mocked_time_in_ms.return_value = 1000
        send_statuses("test_company", "car_1", [self.status])
        mocked_time_in_ms.return_value = 5000
        send_statuses("test_company", "car_1", [self.status])
        cars, code = available_cars(wait=True, since=4500)
        self.assertEqual(len(cars), 0)

    @patch("server.database.time._time_in_ms")
    def test_car_is_not_returned_in_awaited_response_when_its_connection_time_older_than_since_value(
        self, mocked_time_in_ms: Mock
    ):
        set_car_wait_timeout_s(1)
        mocked_time_in_ms.return_value = 1000
        send_statuses("test_company", "test_car", [self.status])

        def list_cars_connected_after_1500():
            cmds, code = available_cars(wait=True, since=1501)
            self.assertEqual(len(cmds), 0)

        def send_test_status():
            mocked_time_in_ms.return_value = 2000
            time.sleep(1)
            send_statuses("test_company", "test_car", [self.status])

        run_in_threads(list_cars_connected_after_1500, send_test_status)

    def tearDown(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")


if __name__ == "__main__":
    unittest.main()

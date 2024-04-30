import sys

sys.path.append("server")

import os
import time
import unittest

from database.connected_cars import clear_connected_cars, serialized_device_id  # type: ignore
from database.database_controller import set_test_db_connection  # type: ignore
from database.time import timestamp  # type: ignore
from fleetv2_http_api.impl.controllers import (  # type: ignore
    send_statuses,
    list_statuses,
    send_commands,
    list_commands
)
from fleetv2_http_api.models.device_id import DeviceId  # type: ignore
from fleetv2_http_api.models.message import Payload, Message  # type: ignore
from fleetv2_http_api.impl.controllers import (  # type: ignore
    set_status_wait_timeout_s,
    set_command_wait_timeout_s
)
from _misc import run_in_threads  # type: ignore


class Test_Ask_For_Statuses_Not_Available_At_The_Time_Of_The_Request(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")
        set_test_db_connection("/example.db")
        clear_connected_cars()
        payload_example = Payload(
            message_type="STATUS", encoding="JSON", data={"message": "Device is running"}
        )
        self.device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Left light")
        self.sdevice_id = serialized_device_id(self.device_id)
        self.status = Message(
            timestamp=123456789,
            device_id=self.device_id,
            payload=payload_example
        )
        set_status_wait_timeout_s(1)

    def test_return_statuses_sent_after_the_request_when_wait_mechanism_is_applied(self):
        def list_test_statuses():
            msg, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 1)

        def send_single_status():
            time.sleep(0.01)
            send_statuses("test_company", "test_car", [self.status.to_dict()])

        run_in_threads(list_test_statuses, send_single_status)

    def test_return_statuses_sent_after_the_request_without_applying_wait_mechanism(self):
        def list_test_statuses():
            msg, code = list_statuses("test_company", "test_car")
            self.assertEqual(
                code, 404
            )  # 404 is returned as the list_statuses does not wait for the statuses to arrive
            self.assertEqual(len(msg), 0)

        def send_single_status():
            time.sleep(0.01)
            send_statuses("test_company", "test_car", [self.status.to_dict()])

        run_in_threads(list_test_statuses, send_single_status)

    def test_return_statuses_sent_after_the_request_with_wait_mechanism_with_timeout_exceeded(self):
        def list_test_statuses():
            set_status_wait_timeout_s(0.01)
            msg, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(code, 404)

        def send_single_status():
            time.sleep(0.02)
            send_statuses("test_company", "test_car", [self.status.to_dict()])

        run_in_threads(list_test_statuses, send_single_status)

    def test_sending_empty_statuses_list_does_not_stop_the_waiting(self):
        def list_test_statuses():
            msg, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 1)

        def send_single_status():
            time.sleep(0.05)
            send_statuses("test_company", "test_car", [self.status.to_dict()])

        def send_no_status():
            time.sleep(0.02)
            send_statuses("test_company", "test_car", [])

        run_in_threads(list_test_statuses, send_no_status, send_single_status)

    def test_sending_second_request_does_not_affect_response_for_the_first_one(self):
        set_status_wait_timeout_s(0.02)

        def list_test_statuses_1():
            _, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(code, 404)

        def list_test_statuses_2():
            time.sleep(0.06)
            _, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)

        def send_single_status():
            time.sleep(0.04)
            send_statuses("test_company", "test_car", [self.status.to_dict()])

        run_in_threads(list_test_statuses_1, list_test_statuses_2, send_single_status)

    def test_sending_second_request_after_statuses_are_available_but_before_timeout(self):
        TIMEOUT = 0.05
        T_FIRST_REQUEST = 0.00
        T_SECOND_REQUEST = 0.08
        T_STATUSES_SENT = 0.1
        set_status_wait_timeout_s(TIMEOUT)

        def list_test_statuses_1():
            time.sleep(T_FIRST_REQUEST)
            msg, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(code, 404)

        def list_test_statuses_2():
            time.sleep(T_SECOND_REQUEST)
            msg, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)

        def send_single_status():
            time.sleep(T_STATUSES_SENT)
            send_statuses("test_company", "test_car", [self.status])

        run_in_threads(list_test_statuses_1, list_test_statuses_2, send_single_status)

    def test_requesting_late_statuses_with_the_since_parameter_newer_than_the_statuses_timestamp_returns_empty_list(
        self,
    ):
        set_status_wait_timeout_s(0.1)

        def list_test_statuses():
            msg, code = list_statuses(
                "test_company", "test_car", wait=True, since=timestamp() + 1000
            )
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 0)

        def send_single_status():
            time.sleep(0.02)
            send_statuses("test_company", "test_car", [self.status])

        run_in_threads(list_test_statuses, send_single_status)

    def test_multiple_requests_for_commands(self):
        set_command_wait_timeout_s(5)
        def list_test_statuses_1():
            statuses, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(len(statuses), 1, "First response contains the status.")

        def list_test_statuses_2():
            statuses, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(len(statuses), 1, "Second response contains the status.")

        def list_test_statuses_3():
            statuses, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(len(statuses), 1, "Third response contains the status.")

        def send_test_statuses():
            time.sleep(0.2)
            response = send_statuses("test_company", "test_car", [self.status])
            self.assertEqual(response[1], 200, "Status was sent successfully.")

        run_in_threads(
            list_test_statuses_1, list_test_statuses_2, list_test_statuses_3, send_test_statuses
        )

    def tearDown(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")


class Test_Ask_For_Commands_Not_Available_At_The_Time_Of_The_Request(unittest.TestCase):
    def setUp(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")
        set_test_db_connection("/example.db")
        clear_connected_cars()
        self.device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Left light")
        self.status = Message(123456789, self.device_id, Payload("STATUS", "JSON", {}))
        self.command = Message(123456789, self.device_id, Payload("COMMAND", "JSON", {}))
        set_command_wait_timeout_s(1)

    def test_return_commands_sent_to_available_device_after_the_request_when_wait_mechanism_is_applied(
        self,
    ):
        set_command_wait_timeout_s(10)

        def list_test_commands():
            msg, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 1)

        def send_single_status_and_command():
            time.sleep(0.01)
            send_statuses("test_company", "test_car", [self.status.to_dict()])
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(list_test_commands, send_single_status_and_command)

    def test_return_commands_sent_after_the_request_without_applying_wait_mechanism(self):
        send_statuses("test_company", "test_car", [self.status.to_dict()])

        def list_test_commands():
            msg, code = list_commands("test_company", "test_car", wait=False)
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 0)  # no commands are present in the moment of the request

        def send_single_command():
            time.sleep(0.01)
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(list_test_commands, send_single_command)

    def test_return_commands_sent_after_the_request_with_wait_mechanism_with_timeout_exceeded(self):
        send_statuses("test_company", "test_car", [self.status.to_dict()])

        def list_test_commands():
            set_command_wait_timeout_s(0.01)
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(cmds), 0)

        def send_single_command():
            time.sleep(0.05)
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(list_test_commands, send_single_command)

    def test_sending_empty_command_list_does_not_stop_the_waiting_process(self):
        send_statuses("test_company", "test_car", [self.status.to_dict()])

        def list_test_commands():
            msg, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 1)

        def send_single_command():
            time.sleep(0.05)
            send_commands("test_company", "test_car", [self.command])

        def send_no_command():
            time.sleep(0.02)
            send_commands("test_company", "test_car", [])

        run_in_threads(list_test_commands, send_no_command, send_single_command)

    def test_sending_second_request_does_not_affect_response_for_the_first_one(self):
        send_statuses("test_company", "test_car", [self.status.to_dict()])
        set_command_wait_timeout_s(0.02)

        def list_test_commands_1():
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(cmds), 0)

        def list_test_commands_2():
            time.sleep(0.06)
            _, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)

        def send_single_command():
            time.sleep(0.04)
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(list_test_commands_1, list_test_commands_2, send_single_command)

    def test_sending_second_request_after_commands_are_available_but_before_timeout(self):
        TIMEOUT = 0.05
        T_FIRST_REQUEST = 0.00
        T_SECOND_REQUEST = 0.08
        T_COMMANDS_SENT = 0.1
        send_statuses("test_company", "test_car", [self.status.to_dict()])
        set_command_wait_timeout_s(TIMEOUT)

        def list_test_commands_1():
            time.sleep(T_FIRST_REQUEST)
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(cmds), 0)

        def list_test_commands_2():
            time.sleep(T_SECOND_REQUEST)
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(cmds), 1)

        def send_single_command():
            time.sleep(T_COMMANDS_SENT)
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(list_test_commands_1, list_test_commands_2, send_single_command)

    def test_sending_commands_to_unavailable_device_does_not_affect_the_waiting(self):
        set_command_wait_timeout_s(0.05)

        def list_test_commands():
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(
                code, 404
            )  # the device did not become available before timeout was exceeded
            self.assertEqual(len(cmds), 0)

        def send_single_command():
            time.sleep(0.01)
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(list_test_commands, send_single_command)

    def test_sending_commands_to_device_that_becomes_available_before_request_timeout(self):
        T_REQUEST = 0.02
        T_DEVICE_AVAILABLE = 0.05
        T_COMMAND_TO_UNAVAIL = 0.01
        T_COMMAND_TO_AVAIL = 0.08
        TIMEOUT = 0.10
        set_command_wait_timeout_s(TIMEOUT)

        def list_test_commands():
            time.sleep(T_REQUEST)
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(cmds), 1)

        def make_device_available():
            time.sleep(T_DEVICE_AVAILABLE)
            send_statuses("test_company", "test_car", [self.status.to_dict()])

        def send_first_single_command():
            time.sleep(T_COMMAND_TO_UNAVAIL)
            send_commands("test_company", "test_car", [self.command])

        def send_second_single_command():
            time.sleep(T_COMMAND_TO_AVAIL)
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(
            list_test_commands,
            send_first_single_command,
            make_device_available,
            send_second_single_command,
        )

    def test_requesting_late_commands_with_the_since_parameter_newer_than_the_commands_timestamp_returns_empty_list(
        self,
    ):
        send_statuses("test_company", "test_car", [self.status.to_dict()])
        set_command_wait_timeout_s(0.1)

        def list_test_commands():
            cmds, code = list_commands(
                "test_company", "test_car", wait=True, since=timestamp() + 1000
            )
            self.assertEqual(code, 200)
            self.assertEqual(len(cmds), 0)

        def send_single_command():
            time.sleep(0.02)
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(list_test_commands, send_single_command)

    def test_requesting_commands_twice(self):
        send_statuses("test_company", "test_car", [self.status.to_dict()])
        command_1 = Message(
            device_id=self.device_id,
            payload=Payload("COMMAND", "JSON", {"message": "First command"}),
        )
        command_2 = Message(
            device_id=self.device_id,
            payload=Payload("COMMAND", "JSON", {"message": "Second command"}),
        )
        set_command_wait_timeout_s(5)

        def list_test_commands():
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(cmds), 1)
            self.assertEqual(cmds[0].payload.data["message"], "First command")
            cmds, code = list_commands(
                "test_company", "test_car", wait=True, since=cmds[0].timestamp + 1
            )
            self.assertEqual(code, 200)
            self.assertEqual(len(cmds), 1)
            self.assertEqual(cmds[0].payload.data["message"], "Second command")

        def send_two_test_commands():
            time.sleep(0.02)
            send_commands("test_company", "test_car", [command_1])
            time.sleep(0.5)
            send_commands("test_company", "test_car", [command_2])

        run_in_threads(list_test_commands, send_two_test_commands)

    def test_multiple_requests_for_commands(self):
        send_statuses("test_company", "test_car", [self.status.to_dict()])
        set_command_wait_timeout_s(5)

        def list_test_commands_1():
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(len(cmds), 1, "First response contains the command.")

        def list_test_commands_2():
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(len(cmds), 1, "Second response contains the command.")

        def list_test_commands_3():
            cmds, code = list_commands("test_company", "test_car", wait=True)
            self.assertEqual(len(cmds), 1, "Third response contains the command.")

        def send_test_commands():
            time.sleep(0.2)
            send_commands("test_company", "test_car", [self.command])

        run_in_threads(
            list_test_commands_1, list_test_commands_2, list_test_commands_3, send_test_commands
        )

    def tearDown(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")


class Test_Waiting_For_Messsages_From_Multiple_Cars(unittest.TestCase):

    def setUp(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")
        set_test_db_connection("/example.db")
        clear_connected_cars()
        payload_example = Payload(
            message_type="STATUS", encoding="JSON", data={"message": "Device is running"}
        )
        self.device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Left light")
        self.sdevice_id = serialized_device_id(self.device_id)
        self.status = Message(
            timestamp=123456789,
            device_id=self.device_id,
            payload=payload_example
        )

    def test_return_statuses_sent_after_the_request_when_wait_mechanism_is_applied(self):
        set_status_wait_timeout_s(1)
        def list_test_statuses_from_car_1():
            time.sleep(0.0)
            msg, code = list_statuses("test_company", "test_car", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 1)

        def list_test_statuses_from_car_2():
            time.sleep(0.0)
            msg, code = list_statuses("test_company", "test_car_2", wait=True)
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 1)

        def send_test_statuses():
            time.sleep(0.01)
            send_statuses("test_company", "test_car", [self.status.to_dict()])
            send_statuses("test_company", "test_car_2", [self.status.to_dict()])

        run_in_threads(list_test_statuses_from_car_1, list_test_statuses_from_car_2, send_test_statuses)

    def tearDown(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")

if __name__ == "__main__":
    unittest.main()

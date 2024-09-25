import unittest
from unittest.mock import patch, Mock
import subprocess
import time
import sys

sys.path.append(".")

import server.database.connection as _connection
from server.fleetv2_http_api.models import DeviceId, Payload, Message
from server.enums import MessageType
from server.fleetv2_http_api.impl.controllers import (
    list_commands,
    list_statuses,
    send_commands,
    send_statuses
)
import server.database.security as _security
from server.fleetv2_http_api.controllers.security_controller import info_from_AdminAuth

from tests._utils.logs import clear_logs


class Test_API_After_Restart_Of_Database(unittest.TestCase):
    def setUp(self) -> None:
        clear_logs()
        subprocess.run(["docker", "compose", "down", "postgresql-database"])
        subprocess.run(["docker", "compose", "up", "postgresql-database", "-d"])
        time.sleep(1.5)
        _connection.set_db_connection(
            dblocation="localhost",
            port="5432",
            db_name="postgres",
            username="postgres",
            password="1234"
        )

    def test_no_statuses_or_commands_after(self) -> None:
        device_id = DeviceId(1, 1, "test", "Test")
        status_payload = Payload.from_dict({"message_type": MessageType.STATUS, "encoding": "JSON", "data": {}})
        command_payload = Payload.from_dict({"message_type": MessageType.COMMAND, "encoding": "JSON", "data": {}})
        status = Message(device_id=device_id, payload=status_payload)
        command = Message(device_id=device_id, payload=command_payload)
        send_statuses("company_x", "car_a", [status])
        send_commands("company_x", "car_a", [command])
        response = list_commands("company_x", "car_a")
        self.assertEqual(len(response[0]), 1)
        self.assertEqual(response[1], 200)

        subprocess.run(["docker", "compose", "down", "postgresql-database"])
        subprocess.run(["docker", "compose", "up", "postgresql-database", "-d"])
        time.sleep(1.5)
        response = list_statuses("company_x", "car_a")
        self.assertEqual(response, ([], 404))
        response = list_commands("company_x", "car_a")
        self.assertEqual(response, ([], 404))

    def test_status_and_command_can_be_sent_after(self) -> None:
        subprocess.run(["docker", "compose", "down", "postgresql-database"])
        subprocess.run(["docker", "compose", "up", "postgresql-database", "-d"])
        time.sleep(1.5)

        device_id = DeviceId(1, 1, "test", "Test")
        status_payload = Payload.from_dict({"message_type": MessageType.STATUS, "encoding": "JSON", "data": {}})
        status = Message(device_id=device_id, payload=status_payload)
        command_payload = Payload.from_dict({"message_type": MessageType.COMMAND, "encoding": "JSON", "data": {}})
        command = Message(device_id=device_id, payload=command_payload)
        send_statuses("company_x", "car_a", [status])
        send_commands("company_x", "car_a", [command])
        response = list_statuses("company_x", "car_a")
        self.assertEqual(len(response[0]), 1)
        self.assertEqual(response[1], 200)
        response = list_commands("company_x", "car_a")
        self.assertEqual(len(response[0]), 1)
        self.assertEqual(response[1], 200)

    @patch("server.database.security._generate_key")
    def test_api_key_is_still_reported_as_working_by_api_until_attempting_to_read_messages(self, generate_key: Mock):
        generate_key.return_value = "0123465798"
        _security.add_admin_key("test_key")
        response = _security.get_admin("0123465798")
        assert response is not None
        self.assertEqual(response.name, "test_key")

        subprocess.run(["docker", "compose", "down", "postgresql-database"])
        subprocess.run(["docker", "compose", "up", "postgresql-database", "-d"])
        time.sleep(1.5)

        # The key is still reported as working by the API
        assert response is not None
        self.assertEqual(response.name, "test_key")

        # But when trying to read messages, the key is no longer valid
        list_statuses("company_x", "car_a")
        response = _security.get_admin("0123465798")
        self.assertIsNone(response)

    @patch("server.database.security._generate_key")
    def test_info_admin_auth_returns_invalid_dict_if_database_is_out(self, generate_key: Mock) -> None:
        generate_key.return_value = "0123465798"
        _security.add_admin_key("test_key")
        response = _security.get_admin("0123465798")
        assert response is not None
        self.assertEqual(response.name, "test_key")

        subprocess.run(["docker", "compose", "down", "postgresql-database"])
        time.sleep(1.5)

        # this clears up cached api keys
        list_statuses("company_x", "car_a")

        response = info_from_AdminAuth("0123465798")
        self.assertIsNotNone(response)

    def tearDown(self):
        subprocess.run(["docker", "compose", "down", "postgresql-database"])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
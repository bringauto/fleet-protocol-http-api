import unittest
from unittest.mock import patch, Mock
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType, EncodingType

from server.database.database_controller import remove_old_messages


class Test_Making_Car_Available_By_Sending_First_Status(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_dev", name="Test")
        self.payload = Payload(
            message_type=MessageType.STATUS,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        self.status = Message(device_id=self.device_id, payload=self.payload)
        self.test_car = {"company_name": "test_company", "car_name": "test_car"}

    def test_test_car_is_initially_not_among_available_cars(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get("/cars")
            self.assertEqual(response.json, [])

    def test_viewing_status_of_nonexisting_car_under_existing_company_returns_404_and_empty_list(
        self,
    ) -> None:
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[self.status])
            response = client.get("/status/test_company/test_car_2")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, [])

    def test_sending_status_makes_car_available(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/status/test_company/test_car", json=[self.status])
            self.assertEqual(response.status_code, 200)
            response = client.get("/cars")
            self.assertEqual(response.json, [self.test_car])

    def test_sending_first_status_for_another_car_of_the_same_company_is_allowed(self):
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[self.status])
            response = client.post("/status/test_company/test_car_2", json=[self.status])
            self.assertEqual(response.status_code, 200)
            response = client.get("/cars")
            self.assertEqual(
                response.json,
                [
                    {"company_name": "test_company", "car_name": "test_car"},
                    {"company_name": "test_company", "car_name": "test_car_2"},
                ],
            )

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_retrieving_sent_status(self, mock_timestamp: Mock) -> None:
        mock_timestamp.return_value = 11111
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[self.status])
            response = client.get("/status/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 11111,
                        "device_id": {"module_id": 7, "type": 8, "role": "test_dev", "name": "Test"},
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    }
                ],
            )

    def test_retrieving_status_for_none_existing_car_returns_404_and_empty_list(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get("/status/test_company/test_car")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, [])

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Sending_And_Viewing_Command_For_Available_Car(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_dev", name="Test")
        status_payload = Payload(
            message_type=MessageType.STATUS,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        command_payload_1 = Payload(
            message_type=MessageType.COMMAND,
            encoding="JSON",
            data={"command": "start"},
        )
        command_payload_2 = Payload(
            message_type=MessageType.COMMAND,
            encoding="JSON",
            data={"command": "continue"},
        )
        command_payload_3 = Payload(
            message_type=MessageType.COMMAND,
            encoding="JSON",
            data={"command": "stop"},
        )
        command_payload_4 = Payload(
            message_type=MessageType.COMMAND,
            encoding="JSON",
            data={"command": "stay"},
        )
        self.status = Message(device_id=self.device_id, payload=status_payload)
        self.command_1 = Message(device_id=self.device_id, payload=command_payload_1)
        self.command_2 = Message(device_id=self.device_id, payload=command_payload_2)
        self.command_3 = Message(device_id=self.device_id, payload=command_payload_3)
        self.command_4 = Message(device_id=self.device_id, payload=command_payload_4)

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_retrieving_commands_succesfully_sent_to_available_car(
        self, mock_timestamp: Mock
    ) -> None:
        with self.app.app.test_client() as client:
            mock_timestamp.return_value = 1000
            client.post("/status/test_company/test_car", json=[self.status])

            mock_timestamp.return_value = 1234
            client.post("/command/test_company/test_car", json=[self.command_1])
            mock_timestamp.return_value = 1235
            client.post("/command/test_company/test_car", json=[self.command_2])
            mock_timestamp.return_value = 1236
            client.post("/command/test_company/test_car", json=[self.command_3, self.command_4])

            response = client.get("/command/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 1234,
                        "device_id": {"module_id": 7, "type": 8, "role": "test_dev", "name": "Test"},
                        "payload": {"message_type": "COMMAND", "encoding": "JSON", "data": {"command": "start"}},
                    },
                    {
                        "timestamp": 1235,
                        "device_id": {"module_id": 7, "type": 8, "role": "test_dev", "name": "Test"},
                        "payload": {"message_type": "COMMAND", "encoding": "JSON", "data": {"command": "continue"}},
                    },
                    {
                        "timestamp": 1236,
                        "device_id": {"module_id": 7, "type": 8, "role": "test_dev", "name": "Test"},
                        "payload": {"message_type": "COMMAND", "encoding": "JSON", "data": {"command": "stop"}},
                    },
                    {
                        "timestamp": 1236,
                        "device_id": {"module_id": 7, "type": 8, "role": "test_dev", "name": "Test"},
                        "payload": {"message_type": "COMMAND", "encoding": "JSON", "data": {"command": "stay"}},
                    }
                ],
            )

            response = client.get("/command/test_company/test_car?since=1235")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [
                {
                    "timestamp": 1235,
                    "device_id": {"module_id": 7, "type": 8, "role": "test_dev", "name": "Test"},
                    "payload": {"message_type": "COMMAND", "encoding": "JSON", "data": {"command": "continue"}},
                },
                {
                    "timestamp": 1236,
                    "device_id": {"module_id": 7, "type": 8, "role": "test_dev", "name": "Test"},
                    "payload": {"message_type": "COMMAND", "encoding": "JSON", "data": {"command": "stop"}},
                },
                {
                    "timestamp": 1236,
                    "device_id": {"module_id": 7, "type": 8, "role": "test_dev", "name": "Test"},
                    "payload": {"message_type": "COMMAND", "encoding": "JSON", "data": {"command": "stay"}},
                }
            ])

    @patch("server.fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_commands_and_automatically_cleaning_them_up(self, mock_timestamp: Mock):
       with self.app.app.test_client() as client:
            mock_timestamp.return_value = 0
            client.post("/status/test_company/test_car", json=[self.status])
            mock_timestamp.return_value = 1
            client.post("/command/test_company/test_car", json=[self.command_1])
            mock_timestamp.return_value = 2
            client.post("/command/test_company/test_car", json=[self.command_2])

            remove_old_messages(current_timestamp=1000000000000000)

            client.post("/status/test_company/test_car", json=[self.status])
            client.post("/command/test_company/test_car", json=[self.command_3])
            client.post("/command/test_company/test_car", json=[self.command_4])
            response = client.get("/command/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            assert response.json is not None
            self.assertEqual(len(response.json), 2)
            self.assertEqual(response.json[0]["payload"]["data"]["command"], "stop")
            self.assertEqual(response.json[1]["payload"]["data"]["command"], "stay")


    def tearDown(self) -> None:  # pragma: no cover
        self.app.clear_all()


class Test_Sending_And_Viewing_Commands_For_Unavailable_Car(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_dev", name="Test")
        command_payload = Payload(
            message_type=MessageType.COMMAND,
            encoding="JSON",
            data={"command": "start"},
        )
        self.command = Message(device_id=self.device_id, payload=command_payload)

    def test_retrieving_command_for_nonexisting_car_returns_404_and_empty_list(self) -> None:
        with self.app.app.test_client() as client:
            response = client.get("/command/test_company/test_car")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, [])

    def test_sending_command_to_nonexistent_car_returns_404(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/command/test_company/test_car", json=[self.command])
            self.assertEqual(response.status_code, 404)

    def tearDown(self) -> None:  # pragma: no cover
        self.app.clear_all()


class Test_Sending_And_Viewing_Statuses_To_Multiple_Cars(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_dev", name="Test")
        status_payload = Payload(
            message_type=MessageType.STATUS,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        self.status_1 = Message(device_id=self.device_id, payload=status_payload)
        self.status_2 = Message(device_id=self.device_id, payload=status_payload)

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_statuses_to_mutliple_cars(self, mock_timestamp: Mock) -> None:
        with self.app.app.test_client() as client:
            mock_timestamp.return_value = 111
            client.post("/status/test_company/test_car", json=[self.status_1])
            mock_timestamp.return_value = 222
            client.post("/status/test_company/test_car_2", json=[self.status_2])
            response = client.get("/cars")
            self.assertEqual(
                response.json,
                [
                    {"company_name": "test_company", "car_name": "test_car"},
                    {"company_name": "test_company", "car_name": "test_car_2"},
                ],
            )
            response = client.get("/status/test_company/test_car")
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 111,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_dev",
                            "name": "Test",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    }
                ],
            )
            response = client.get("/status/test_company/test_car_2")
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 222,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_dev",
                            "name": "Test",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    }
                ],
            )
            self.assertEqual(response.status_code, 200)

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Sending_And_Viewing_Statuses_Sent_To_Multiple_Devices_On_Single_Car(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        device_A_id = DeviceId(module_id=7, type=8, role="test_device_l", name="Test Device A")
        device_B_id = DeviceId(module_id=7, type=9, role="test_device_r", name="Test Device B")
        device_C_id = DeviceId(module_id=14, type=8, role="test_dev", name="Test Device C")
        status_payload_A = Payload(
            message_type=MessageType.STATUS,
            encoding=EncodingType.JSON,
            data={"phone_number": "1234567890"},
        )
        status_payload_B = Payload(
            message_type=MessageType.STATUS,
            encoding=EncodingType.JSON,
            data={"phone_number": "1234567890"},
        )
        status_payload_C = Payload(
            message_type=MessageType.STATUS, encoding=EncodingType.BASE64, data={}
        )
        self.status_1 = Message(device_id=device_A_id, payload=status_payload_A)
        self.status_2 = Message(device_id=device_B_id, payload=status_payload_B)
        self.status_3 = Message(device_id=device_C_id, payload=status_payload_C)

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_two_statuses_to_different_devices_is_possible(
        self, mock_timestamp: Mock
    ) -> None:
        with self.app.app.test_client() as client:
            mock_timestamp.return_value = 111
            client.post("/status/test_company/test_car", json=[self.status_1])
            mock_timestamp.return_value = 222
            client.post("/status/test_company/test_car", json=[self.status_2])
            response = client.get("/status/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 111,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_device_l",
                            "name": "Test Device A",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    },
                    {
                        "timestamp": 222,
                        "device_id": {
                            "module_id": 7,
                            "type": 9,
                            "role": "test_device_r",
                            "name": "Test Device B",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    },
                ],
            )

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_statuses_to_different_modules_is_possible(self, mock_timestamp: Mock) -> None:
        with self.app.app.test_client() as client:
            mock_timestamp.return_value = 111
            client.post("/status/test_company/test_car", json=[self.status_1])
            mock_timestamp.return_value = 222
            client.post("/status/test_company/test_car", json=[self.status_3])

            response = client.get("/status/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 111,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_device_l",
                            "name": "Test Device A",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    },
                    {
                        "timestamp": 222,
                        "device_id": {
                            "module_id": 14,
                            "type": 8,
                            "role": "test_dev",
                            "name": "Test Device C",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "BASE64",
                            "data": {},
                        },
                    },
                ],
            )

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Sending_Multiple_Statuses_To_The_Same_Car_At_Once(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        device_A_id = DeviceId(module_id=7, type=8, role="test_device_x", name="Test Device_X")
        device_B_id = DeviceId(module_id=9, type=9, role="test_device_y", name="Test Device Y")
        status_payload_A = Payload(
            message_type=MessageType.STATUS,
            encoding=EncodingType.JSON,
            data={"phone_number": "1234567890"},
        )
        status_payload_B = Payload(
            message_type=MessageType.STATUS,
            encoding=EncodingType.JSON,
            data={"phone_number": "1234567890"},
        )
        self.status_1 = Message(device_id=device_A_id, payload=status_payload_A)
        self.status_2 = Message(device_id=device_B_id, payload=status_payload_B)

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_two_statuses_at_once_is_possible_for_two_distinct_devices(
        self, mock_timestamp: Mock
    ) -> None:
        with self.app.app.test_client() as client:
            mock_timestamp.return_value = 11111
            response = client.post(
                "/status/test_company/test_car", json=[self.status_1, self.status_2]
            )
            self.assertEqual(response.status_code, 200)
            response = client.get("/status/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 11111,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_device_x",
                            "name": "Test Device_X",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    },
                    {
                        "timestamp": 11111,
                        "device_id": {
                            "module_id": 9,
                            "type": 9,
                            "role": "test_device_y",
                            "name": "Test Device Y",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    },
                ],
            )

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_one_status_twice_in_one_request_is_allowed(self, mock_timestamp: Mock) -> None:
        with self.app.app.test_client() as client:
            mock_timestamp.return_value = 11111
            response = client.post(
                "/status/test_company/test_car", json=[self.status_1, self.status_1]
            )
            self.assertEqual(response.status_code, 200)
            response = client.get("/status/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 11111,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_device_x",
                            "name": "Test Device_X",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    },
                    {
                        "timestamp": 11111,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_device_x",
                            "name": "Test Device_X",
                        },
                        "payload": {
                            "message_type": "STATUS",
                            "encoding": "JSON",
                            "data": {"phone_number": "1234567890"},
                        },
                    },
                ],
            )

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Sending_Multiple_Commands_To_The_Same_Car_At_Once(unittest.TestCase):
    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def setUp(self, mock_timestamp: Mock) -> None:
        self.maxDiff = 1000
        self.app = _app.get_test_app(db_location="test_db.db", base_url="/v2/protocol/")
        self.device_1_id = DeviceId(module_id=7, type=8, role="test_dev", name="Test Device 1")
        self.device_2_id = DeviceId(module_id=9, type=5, role="test_dev", name="Test Device 2")
        status_payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
        command_payload_A = Payload(MessageType.COMMAND, "JSON", {"command": "start"})
        command_payload_B = Payload(MessageType.COMMAND, "JSON", {"command": "continue"})
        status_1 = Message(device_id=self.device_1_id, payload=status_payload)
        status_2 = Message(device_id=self.device_2_id, payload=status_payload)
        self.command_A = Message(device_id=self.device_1_id, payload=command_payload_A)
        self.command_B = Message(device_id=self.device_2_id, payload=command_payload_B)

        mock_timestamp.return_value = 11111
        with self.app.app.test_client() as client:
            client.post("/status/test_company/test_car", json=[status_1, status_2])
            client.get("/v2/protocol/available-devices/test_company/test_car")

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_two_commands_to_the_same_device_is_allowed(self, mock_timestamp: Mock):
        mock_timestamp.return_value = 11112
        with self.app.app.test_client() as client:
            response = client.post(
                "/command/test_company/test_car", json=[self.command_A, self.command_B]
            )
            self.assertEqual(response.status_code, 200)
            response = client.get("/command/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)  # type: ignore
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 11112,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_dev",
                            "name": "Test Device 1",
                        },
                        "payload": {
                            "message_type": "COMMAND",
                            "encoding": "JSON",
                            "data": {"command": "start"},
                        },
                    },
                    {
                        "timestamp": 11112,
                        "device_id": {
                            "module_id": 9,
                            "type": 5,
                            "role": "test_dev",
                            "name": "Test Device 2",
                        },
                        "payload": {
                            "message_type": "COMMAND",
                            "encoding": "JSON",
                            "data": {"command": "continue"},
                        },
                    },
                ],
            )

    @patch("fleetv2_http_api.impl.controllers._timestamp")
    def test_sending_command_twice_in_one_request_is_allowed(self, mock_timestamp: Mock):
        mock_timestamp.return_value = 11112
        with self.app.app.test_client() as client:
            response = client.post(
                "/command/test_company/test_car", json=[self.command_A, self.command_A]
            )
            self.assertEqual(response.status_code, 200)
            response = client.get("/command/test_company/test_car")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json), 2)  # type: ignore
            self.assertEqual(
                response.json,
                [
                    {
                        "timestamp": 11112,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_dev",
                            "name": "Test Device 1",
                        },
                        "payload": {
                            "message_type": "COMMAND",
                            "encoding": "JSON",
                            "data": {"command": "start"},
                        },
                    },
                    {
                        "timestamp": 11112,
                        "device_id": {
                            "module_id": 7,
                            "type": 8,
                            "role": "test_dev",
                            "name": "Test Device 1",
                        },
                        "payload": {
                            "message_type": "COMMAND",
                            "encoding": "JSON",
                            "data": {"command": "start"},
                        },
                    },
                ],
            )

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Mismatch_Between_Endpoint_And_Message_Type(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_dev", name="Test")
        self.status_payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
        self.command_payload = Payload(MessageType.COMMAND, "JSON", {"command": "start"})
        self.status_1 = Message(device_id=self.device_id, payload=self.status_payload)
        self.status_2 = Message(device_id=self.device_id, payload=self.status_payload)
        self.command = Message(device_id=self.device_id, payload=self.command_payload)

    def test_sending_status_to_command_endpoint_returns_400(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/command/company/test_car", json=[self.status_1])
            self.assertEqual(response.status_code, 400)

    def test_sending_command_to_status_endpoint_returns_400(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/status/company/test_car", json=[self.command])
            self.assertEqual(response.status_code, 400)

    def test_sending_command_together_with_status_to_status_endpoint_returns_400(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/status/company/test_car", json=[self.status_1, self.command])
            self.assertEqual(response.status_code, 400)

    def test_sending_status_together_with_command_to_command_endpoint_returns_400(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/command/company/test_car", json=[self.status_1, self.command])
            self.assertEqual(response.status_code, 400)

    def test_status_is_not_send_if_it_is_send_together_with_command(self):
        with self.app.app.test_client() as client:
            response = client.post("/status/company/test_car", json=[self.status_1, self.command])
            self.assertEqual(response.status_code, 400)
            response = client.get("/status/company/test_car")
            self.assertEqual(response.status_code, 404)

    def test_command_is_not_send_if_it_is_send_together_with_status(self):
        with self.app.app.test_client() as client:
            client.post("/status/company/test_car", json=[self.status_1])  # make car available
            response = client.post("/command/company/test_car", json=[self.status_2, self.command])
            self.assertEqual(response.status_code, 400)

    def tearDown(self) -> None:
        self.app.clear_all()


class Test_Sending_Empty_List_Of_Messages(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_dev", name="Test")
        self.status_payload = Payload(MessageType.STATUS, "JSON", {"phone": "1234567890"})
        self.command_payload = Payload(MessageType.COMMAND, "JSON", {"command": "start"})
        self.status = Message(device_id=self.device_id, payload=self.status_payload)
        self.command = Message(device_id=self.device_id, payload=self.command_payload)

    def test_sending_empty_list_of_statuses_yields_200(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/status/company/test_car", json=[])
            self.assertEqual(response.status_code, 200)

    def test_sending_empty_list_of_commands_to_available_device_yields_200(self) -> None:
        with self.app.app.test_client() as client:
            client.post("/status/company/test_car", json=[self.status])
            response = client.post("/command/company/test_car", json=[])
            self.assertEqual(response.status_code, 200)

    def test_sending_empty_list_of_commands_to_unavailable_device_yields_404(self) -> None:
        with self.app.app.test_client() as client:
            response = client.post("/command/company/test_car", json=[])
            self.assertEqual(response.status_code, 404)

    def tearDown(self) -> None:
        self.app.clear_all()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

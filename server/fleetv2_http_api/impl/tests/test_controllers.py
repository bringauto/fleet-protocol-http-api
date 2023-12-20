import os
import sys
sys.path.append("server")

from enums import MessageType, EncodingType
import unittest
from unittest.mock import patch, Mock
from sqlalchemy import insert

from database.device_ids import clear_device_ids, serialized_device_id
from database.connection import get_connection_source
from database.database_controller import (
    set_test_db_connection,
    MessageBase,
    remove_old_messages,
    future_command_warning,
    get_available_devices_from_database
)
from fleetv2_http_api.impl.controllers import (
    available_devices, 
    available_cars,
    send_statuses, 
    send_commands, 
    list_statuses, 
    list_commands,
)
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Payload, Message
from fleetv2_http_api.models.module import Module
from fleetv2_http_api.models.car import Car


class Test_Device_Id_Validity(unittest.TestCase):

    def test_devide_id_validity(self):
        id = DeviceId(module_id=42, type=2, role="light", name="Left light")
        # module id cannot be negative
        id.module_id = 43
        self.assertEqual(id.module_id, 43)
        with self.assertRaises(ValueError): id.module_id = -15
        # type cannot be negative
        id.type = 3
        self.assertEqual(id.type, 3)
        with self.assertRaises(ValueError): id.type = -7
        # role must be nonempty, lowercase and without spaces
        id.role = "new_role"
        self.assertEqual(id.role, "new_role")
        with self.assertRaises(ValueError): id.role = ""
        with self.assertRaises(ValueError): id.role = "role with spaces"
        with self.assertRaises(ValueError): id.role = "Role"


class Test_Listing_Available_Devices_And_Cars(unittest.TestCase):
    
    def setUp(self) -> None:
        set_test_db_connection("/:memory:")
        payload_example = Payload(
            message_type=MessageType.STATUS_TYPE, 
            encoding=EncodingType.JSON, 
            data={"message":"Device is running"}
        )
        self.device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Left light")
        self.status_example = Message(
            timestamp=123456789,
            device_id=self.device_id,
            payload=payload_example
        )
        clear_device_ids()

    def test_device_is_considered_available_if_at_least_one_status_is_in_the_database(self):
        self.assertEqual(available_devices("test_company", "test_car"), ([], 404))
        send_statuses("test_company", "test_car", messages=[self.status_example])
        self.assertEqual(
            available_devices("test_company", "test_car")[0], 
            [
                Module(module_id=42, device_list=[self.device_id]),
            ]
        )
        self.assertEqual(available_devices("other_company", "some_car"), ([], 404))
    
    def test_car_is_considered_available_if_at_least_one_of_its_devices_are_available(self):
        self.assertListEqual(available_cars(), [])
        response, code = send_statuses(
            company_name="test_company", 
            car_name="test_car",
            messages=[self.status_example]
        )
        self.assertEqual(code, 200)
        self.assertListEqual(available_cars(), [Car("test_company","test_car")])

    def test_listing_device_for_unavailable_car_returns_empty_list_and_code_404(self):
        device_id = DeviceId(module_id=18, type=3, role="available_device", name="Available device")
        status = Message(
            timestamp=456, 
            device_id=device_id, 
            payload=Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        )
        send_statuses("the_company", "available_car", messages=[status])
        self.assertEqual(available_devices("the_company", "unavailable_car"), ([], 404))
        self.assertEqual(available_devices("no_company", "unavailable_car"), ([], 404))

    def test_listing_devices_for_particular_module(self):
        device_1_id = DeviceId(module_id=18, type=3, role="available_device", name="Available device")
        status_1 = Message(
            timestamp=456, 
            device_id=device_1_id, 
            payload=Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        )
        device_2_id = DeviceId(module_id=173, type=3, role="available_device", name="Available device")
        status_2 = Message(
            timestamp=498, 
            device_id=device_2_id, 
            payload=Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        )
        send_statuses("the_company", "available_car", messages=[status_1])
        send_statuses("the_company", "available_car", messages=[status_2])
        self.assertEqual(
            available_devices("the_company", "available_car", module_id=18)[0], 
            Module(module_id=18, device_list=[device_1_id])
        )
        self.assertEqual(
            available_devices("the_company", "available_car", module_id=173)[0], 
            Module(module_id=173, device_list=[device_2_id])
        )


class Test_Sending_And_Listing_Multiple_Messages(unittest.TestCase):

    def setUp(self) -> None:
        set_test_db_connection("/:memory:")
        self.device_id = DeviceId(module_id=42, type=7, role="test_device", name="Test Device X")
        self.status_example = Message(
            timestamp=123456789,
            device_id=DeviceId(module_id=42, type=7, role="test_device", name="Test Device X"),
            payload=Payload(
                message_type=MessageType.STATUS_TYPE, 
                encoding=EncodingType.JSON, 
                data={"message":"Device is running"}
            )
        )
        self.command_example = Message(
            timestamp = 124879465,
            device_id = DeviceId(module_id=42, type=7, role="test_device", name="Test Device X"),
            payload = Payload(
                message_type=MessageType.COMMAND_TYPE, 
                encoding=EncodingType.JSON, 
                data={"message":"Beep"}
            )
        )
        clear_device_ids()

    def test_listing_sent_statuses(self)->None:
        send_statuses("test_company", "test_car", messages=[self.status_example])
        statuses, code = list_statuses("test_company", "test_car")
        self.assertEqual(len(statuses), 1)
        self.assertEqual(code, 200)
        status = statuses[0]
        self.assertEqual(status.device_id.module_id, self.status_example.device_id.module_id)
        self.assertEqual(status.device_id.type, self.status_example.device_id.type)
        self.assertEqual(status.device_id.role, self.status_example.device_id.role)
        self.assertEqual(status.payload, self.status_example.payload)

    def test_sending_empty_list_of_statuses_does_not_affect_list_of_statuses_returned_from_database(self)->None:
        send_statuses("test_company", "test_car", messages=[self.status_example])
        statuses_before = list_statuses("test_company", "test_car")
        send_statuses("test_company", "test_car", messages=[])
        statuses_after = list_statuses("test_company", "test_car")
        self.assertEqual(statuses_before, statuses_after)

    def test_sent_commands_to_available_devices(self)->None:
        send_statuses(
            company_name="test_company", 
            car_name="test_car",
            messages=[self.status_example]
        )
        send_commands(
            company_name="test_company", 
            car_name="test_car",
            messages=[self.command_example]
        )
        commands, code = list_commands("test_company","test_car")
        self.assertEqual(code, 200)
        self.assertEqual(len(commands), 1)
        cmd = commands[0]
        self.assertEqual(cmd.device_id.module_id, self.command_example.device_id.module_id)
        self.assertEqual(cmd.device_id.type, self.command_example.device_id.type)
        self.assertEqual(cmd.device_id.role, self.command_example.device_id.role)
        self.assertEqual(cmd.payload, self.command_example.payload)

    def test_sending_commands_to_unavailable_module_car_or_company_returns_code_404(self)->None:
        send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            messages=[self.status_example]
        )

        id_of_device_in_nonexistent_module = DeviceId(
            module_id=1111111, 
            type=7, 
            role="test_device", 
            name="Test Device X"
        )
        command_of_device_in_nonexistent_module = Message(
            timestamp = 124879465,
            device_id=id_of_device_in_nonexistent_module, 
            payload=self.command_example.payload
        )

        response, code = send_commands(
            company_name="test_company", 
            car_name="test_car", 
            messages=[command_of_device_in_nonexistent_module]
        )
        self.assertEqual(code, 404)

        response, code = send_commands(
            company_name="test_company", 
            car_name="nonexistent_car",
            messages=[self.command_example]
        )
        self.assertEqual(code, 404)

        response, code = send_commands(
            company_name="nonexistent_company", 
            car_name="test_car",
            messages=[self.command_example]
        )
        self.assertEqual(code, 404)

    def test_sending_empty_list_of_commands_does_not_affect_list_of_commands_returned_from_database(self)->None:
        send_commands("test_company", "test_car", messages=[self.command_example])
        commands_before = list_commands("test_company", "test_car")

        send_commands("test_company", "test_car", messages=[])
        commands_after = list_commands("test_company", "test_car")
        self.assertEqual(commands_before, commands_after)

    def test_sending_commands_sent_to_nonexistent_device_returns_code_404(self)->None:
        response = send_commands(
            company_name="test_company", 
            car_name="test_car",
            messages=[self.command_example]
        )
        self.assertEqual(response[1], 404)


class Test_Timestamp_Of_A_Sent_Message_Is_Set_To_Time_Of_Its_Sending(unittest.TestCase):

    @patch('database.time._time_in_ms')
    def test_status_original_timestamp_is_set_to_the_current_timestamp_when_sending_the_status(self, mock_time_ms:Mock):
        payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        message_1 = Message(timestamp=10, device_id=device_id, payload = payload)

        mock_time_ms.return_value = 25       
        send_statuses("test_company", "test_car", messages=[message_1])
        statuses, code = list_statuses("test_company", "test_car")
        self.assertEqual(statuses[0].timestamp, 25)


class Test_Options_For_Listing_Multiple_Statuses(unittest.TestCase):

    @patch('database.time._time_in_ms')
    def setUp(self, mock_time_in_ms:Mock) -> None:
        set_test_db_connection("/:memory:")
        payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        
        message_1 = Message(timestamp=10, device_id=device_id, payload = payload)
        message_2 = Message(timestamp=20, device_id=device_id, payload = payload)
        message_3 = Message(timestamp=37, device_id=device_id, payload = payload)

        mock_time_in_ms.return_value = 10
        send_statuses("company", "car", messages=[message_1])
        mock_time_in_ms.return_value = 20
        send_statuses("company", "car", messages=[message_2])
        mock_time_in_ms.return_value = 37
        send_statuses("company", "car", messages=[message_3])

    def test_by_default_only_the_newest_status_is_returned(self):
        statuses, _ = list_statuses("company", "car")
        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[-1].timestamp, 37)

    def test_since_parameter_equal_to_newest_status_timestamp_yields_the_newest_status(self):
        statuses, _ = list_statuses("company", "car", since=37)
        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[-1].timestamp, 37)

    def test_since_parameter_larger_to_newest_status_timestamp_yields_empty_status_list(self):
        statuses, _ = list_statuses("company", "car", since=38)
        self.assertEqual(len(statuses), 0)

    def test_since_option_returns_all_statuses_inclusivelly_newer_than_the_specified_time(self):
        statuses, _ = list_statuses("company", "car", since=20)
        self.assertEqual(statuses[0].timestamp, 20)
        self.assertEqual(statuses[1].timestamp, 37)

    def test_if_all_is_specified_all_statuses_are_returned(self):
        # any value passed as 'all' attribute makes the list_statuses to return all the statuses
        statuses, _ = list_statuses("company", "car", all_available="")
        self.assertEqual(len(statuses), 3)
        self.assertEqual(statuses[0].timestamp, 10)
        self.assertEqual(statuses[1].timestamp, 20)
        self.assertEqual(statuses[2].timestamp, 37)


class Test_Options_For_Listing_Multiple_Commands(unittest.TestCase):

    @patch('database.time._time_in_ms')
    def setUp(self, mock_time_in_ms:Mock) -> None:
        set_test_db_connection("/:memory:")
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        status_payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        command_payload = Payload(message_type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"message":"Beep"})

        status = Message(timestamp=0, device_id=device_id, payload=status_payload)
        command_1 = Message(timestamp=0, device_id=device_id, payload=command_payload)
        command_2 = Message(timestamp=0, device_id=device_id, payload=command_payload)
        command_3 = Message(timestamp=0, device_id=device_id, payload=command_payload)

        mock_time_in_ms.return_value = 10
        send_statuses("company", "car", [status])
        mock_time_in_ms.return_value = 20
        send_commands("company", "car", [command_1])
        mock_time_in_ms.return_value = 30
        send_commands("company", "car", [command_2])
        mock_time_in_ms.return_value = 45
        send_commands("company", "car", [command_3])

    def test_by_default_only_the_newest_command_is_returned(self):
        commands, code = list_commands("company", "car")
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[-1].timestamp, 45)

    def test_since_parameter_equal_to_newest_command_timestamp_yields_the_oldest_command(self):
        commands, code = list_commands("company", "car", since=45)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].timestamp, 45)

    def test_since_parameter_smaller_than_newest_command_timestamp_yields_empty_command_list(self):
        commands, code = list_commands("company", "car", since=46)
        self.assertEqual(len(commands), 0)
    
    def test_since_option_returns_all_commands_inclusivelly_newer_than_the_specified_time(self):
        commands, code = list_commands("company", "car", since=30)
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].timestamp, 30)
        self.assertEqual(commands[1].timestamp, 45)

    def test_if_all_is_specified_all_commands_are_returned(self):
        commands, code = list_commands("company", "car", all_available="")
        self.assertEqual(len(commands), 3)
        self.assertEqual(commands[0].timestamp, 20)
        self.assertEqual(commands[1].timestamp, 30)
        self.assertEqual(commands[2].timestamp, 45)


class Test_Cleaning_Up_Commands(unittest.TestCase):

    DATA_RETENTION_PERIOD = MessageBase.data_retention_period_ms

    def setUp(self) -> None:
        set_test_db_connection("/:memory:")
        clear_device_ids()
        self.device_id = DeviceId(module_id=42, type=5, role="left_light", name="Left light")
        self.status_payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is conected"})
        self.command_payload = Payload(message_type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"message":"Beep"})

    @patch('database.time._time_in_ms')
    def test_cleaning_up_commands(self, mock_time_in_ms:Mock):
        status = Message(timestamp=0, device_id=self.device_id, payload=self.status_payload)
        command_1 = Message(timestamp=10, device_id=self.device_id, payload=self.command_payload)
        command_2 = Message(timestamp=20, device_id=self.device_id, payload=self.command_payload)

        mock_time_in_ms.return_value = 0
        send_statuses("company", "car", [status])
        mock_time_in_ms.return_value = 10
        send_commands("company", "car", [command_1])
        mock_time_in_ms.return_value = 20
        send_commands("company", "car", [command_2])

        self.assertEqual(len(list_statuses("company", "car", all_available="")[0]), 1)
        self.assertEqual(len(list_commands("company", "car", all_available="")[0]), 2)

        mock_time_in_ms.return_value = self.DATA_RETENTION_PERIOD+20
        remove_old_messages(mock_time_in_ms.return_value)

        self.assertEqual(len(list_statuses("company", "car", all_available="")[0]), 0)
        self.assertEqual(len(list_commands("company", "car", all_available="")[0]), 0)
        
        mock_time_in_ms.return_value += 5 
        
        # the following status is considered to be the FIRST status for given device and after sending it, 
        # all commands previously sent to this device have to be removed
        send_statuses("company", "car", [status])
        self.assertEqual(len(list_statuses("company", "car", all_available="")[0]), 1)
        self.assertEqual(len(list_commands("company", "car", all_available="")[0]), 0)

    @patch('database.time._time_in_ms')
    def test_cleaning_up_command_with_newer_timestamp_relative_to_the_first_status_raises_warning(self, mock_time_in_ms:Mock):
        status = Message(timestamp=0, device_id=self.device_id, payload=self.status_payload)
        new_first_status = Message(timestamp=self.DATA_RETENTION_PERIOD + 50, device_id=self.device_id, payload=self.status_payload)
        command_1 = Message(timestamp=self.DATA_RETENTION_PERIOD+30, device_id=self.device_id, payload=self.command_payload)
        # the following timestamp is invalid as it is set to the future relative to the next (FIRST) status
        command_2 = Message(timestamp=self.DATA_RETENTION_PERIOD+100, device_id=self.device_id, payload=self.command_payload)

        mock_time_in_ms.return_value = 0
        send_statuses("company", "car", [status])
        self.assertEqual(
            available_devices("company", "car")[0],
            [Module(module_id=42, device_list=[self.device_id])]
        )
        self.assertEqual(available_cars(),[Car("company", "car")])

        mock_time_in_ms.return_value = self.DATA_RETENTION_PERIOD+30
        send_commands("company", "car", [command_1])
        mock_time_in_ms.return_value = self.DATA_RETENTION_PERIOD+100
        send_commands("company", "car", [command_2])

        remove_old_messages(self.DATA_RETENTION_PERIOD + 10)

        self.assertEqual(len(list_statuses("company", "car", all_available="")[0]), 0)
        # The device is considered to be disconnected and all commands sent to it are then 
        # considered to be removed.
        self.assertEqual(len(list_commands("company", "car", all_available="")[0]), 0)

        self.assertEqual(
            available_devices("company", "car"), 
            ([], 404)
        )
        self.assertEqual(available_cars(), [])

        mock_time_in_ms.return_value = self.DATA_RETENTION_PERIOD + 50
        warnings, code = send_statuses("company", "car", [new_first_status])
        self.assertEqual(len(list_statuses("company", "car", all_available="")[0]), 1)
        self.assertEqual(len(list_commands("company", "car", all_available="")[0]), 0) 

        assert(type(warnings) is str)
        for warning in future_command_warning(
                    timestamp=self.DATA_RETENTION_PERIOD + 100,
                    company_name="company",
                    car_name="car",
                    serialized_device_id= serialized_device_id(self.device_id),
                    payload_data=command_2.payload.data
                ):
            self.assertIn(warning, warnings)


class Test_Listing_Commands_And_Statuses_Of_Nonexistent_Cars(unittest.TestCase):

    def setUp(self) -> None:
        set_test_db_connection("/:memory:")
        device_id = DeviceId(module_id=15, type=3, role="available_device", name="Available device")
        status = Message(
            timestamp=456, 
            device_id=device_id, 
            payload=Payload(
                message_type=MessageType.STATUS_TYPE, 
                encoding=EncodingType.JSON, 
                data={"message":"Device is running"}
            )
        )
        send_statuses(
            company_name="a_company", 
            car_name="a_car", 
            messages=[status]
        )

    def test_listing_statuses_of_nonexistent_company_returns_code_404(self):
        self.assertEqual(list_statuses("nonexistent_company", "a_car"), ([], 404))

    def test_listing_commands_of_nonexistent_company_returns_code_404(self):
        self.assertEqual(list_commands("nonexistent_company", "a_car"), ([], 404))

    def test_listing_statuses_of_nonexistent_car(self):
        self.assertEqual(list_statuses("a_company", "nonexistent_car"), ([], 404))

    def test_listing_commands_of_nonexistent_car(self):
        self.assertEqual(list_commands("a_company", "nonexistent_car"), ([], 404))


class Test_Correspondence_Between_Payload_Type_And_Send_Command_And_Send_Status_Methods(unittest.TestCase):
    
    def setUp(self) -> None:
        if os.path.exists("./example.db"): os.remove("./example.db")
        set_test_db_connection("/example.db")

    def test_send_statuses_accepts_only_statuses(self):
        payload = Payload(message_type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"message":"Beep"})
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        command = Message(timestamp=10, device_id=device_id, payload=payload)
        _, code = send_statuses("test_company", "test_car", [command])
        self.assertEqual(code, 500)

    def test_send_commands_accepts_only_commands(self):
        payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        status = Message(timestamp=10, device_id=device_id, payload=payload)
        _, code = send_commands("test_company", "test_car", [status])
        self.assertEqual(code, 500)

    def tearDown(self) -> None:
        if os.path.exists("./example.db"): os.remove("./example.db")


class Test_Store_Available_Device_Ids_After_Connecting_To_Database_Already_Containing_Data(unittest.TestCase):

    def setUp(self) -> None:
        clear_device_ids()

    def test_list_available_cars(self):
        set_test_db_connection("/:memory:")
        with get_connection_source().begin() as conn:
            stmt = insert(MessageBase.__table__) # type: ignore
            msg_base = MessageBase(
                timestamp=123456789,
                company_name="company_xy",
                car_name="car_abc",
                serialized_device_id="42_7_test_device",
                message_type=MessageType.STATUS_TYPE,
                module_id=42,
                device_type=7,
                device_role="test_device",
                device_name="Test Device",
                payload_encoding=EncodingType.JSON,
                payload_data={"message":"Device is running"}
            )
            data_list = [msg_base.__dict__]
            conn.execute(stmt, data_list)

        get_available_devices_from_database()
        self.assertListEqual(available_cars(), [Car("company_xy", "car_abc")])
        

if __name__=="__main__":
    unittest.main()

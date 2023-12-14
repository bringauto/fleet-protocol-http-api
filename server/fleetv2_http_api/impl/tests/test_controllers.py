# Fleet Protocol v2 HTTP API 
# Copyright (C) 2023 BringAuto s.r.o.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import sys


import unittest
from enums import MessageType, EncodingType
from database.device_ids import clear_device_ids, serialized_device_id
from database.database_controller import set_db_connection
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
        set_db_connection("sqlite","pysqlite","/:memory:")
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
        sdevice_id = serialized_device_id(self.device_id)
        self.assertEqual(available_devices("test_company", "test_car"), ([], 404))

        send_statuses("test_company", "test_car", sdevice_id, messages=[self.status_example])

        self.assertEqual(
            available_devices("test_company", "test_car")[0], 
            [
                Module(module_id=42, device_list=[self.device_id]),
            ]
        )
        self.assertEqual(available_devices("other_company", "some_car"), ([], 404))
    
    def test_car_is_considered_available_if_at_least_one_of_its_devices_are_available(self):
        self.assertListEqual(available_cars(), [])
        device_id = "42_7_test_device_1"
        response, code = send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            sdevice_id=device_id, 
            messages=[self.status_example]
        )
        self.assertEqual(code, 200)
        self.assertListEqual(available_cars(), [Car("test_company","test_car")])

    def test_listing_device_for_unavailable_car_returns_empty_list_and_code_404(self):
        device_id = DeviceId(module_id=18, type=3, role="available_device", name="Available device")
        sdevice_id = serialized_device_id(device_id)
        status = Message(
            timestamp=456, 
            device_id=device_id, 
            payload=Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        )
        send_statuses(
            company_name="the_company", 
            car_name="available_car", 
            sdevice_id=sdevice_id, 
            messages=[status]
        )
        self.assertEqual(available_devices("the_company", "unavailable_car"), ([], 404))
        self.assertEqual(available_devices("no_company", "unavailable_car"), ([], 404))

    def test_listing_devices_for_particular_module(self):
        device_1_id = DeviceId(module_id=18, type=3, role="available_device", name="Available device")
        sdevice_1_id = serialized_device_id(device_1_id)
        status_1 = Message(
            timestamp=456, 
            device_id=device_1_id, 
            payload=Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        )
        device_2_id = DeviceId(module_id=173, type=3, role="available_device", name="Available device")
        sdevice_2_id = serialized_device_id(device_2_id)
        status_2 = Message(
            timestamp=498, 
            device_id=device_2_id, 
            payload=Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        )
        send_statuses(
            company_name="the_company", 
            car_name="available_car", 
            sdevice_id=sdevice_1_id, 
            messages=[status_1]
        )
        send_statuses(
            company_name="the_company", 
            car_name="available_car", 
            sdevice_id=sdevice_2_id, 
            messages=[status_2]
        )
        self.assertEqual(
            available_devices("the_company", "available_car", module_id=18)[0], 
            Module(module_id=18, device_list=[device_1_id])
        )
        self.assertEqual(
            available_devices("the_company", "available_car", module_id=173)[0], 
            Module(module_id=173, device_list=[device_2_id])
        )

    def test_sending_status_with_device_id_not_matching_the_device_id_in_url_raises_exception(self):
        device_id = DeviceId(module_id=18, type=3, role="available_device", name="Available device")
        unmatched_sdevice_id = "19_4_other_device"
        status = Message(
            timestamp=456, 
            device_id=device_id, 
            payload=Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        )
        _, code = send_statuses(
                company_name="the_company", 
                car_name="available_car", 
                sdevice_id=unmatched_sdevice_id, 
                messages=[status]
            )
        self.assertEqual(code, 500)
    
    def test_listing_available_devices_for_nonexistent_module_returns_code_404(self):
        device_id = DeviceId(module_id=18, type=3, role="available_device", name="Available device")
        sdevice_id = serialized_device_id(device_id)
        status = Message(
            timestamp=456, 
            device_id=device_id, 
            payload=Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        )
        send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            sdevice_id=sdevice_id, 
            messages=[status]
        )
        self.assertEqual(
            available_devices("test_company", "test_car", module_id=4999999), 
            ([], 404)
        )


class Test_Sending_And_Listing_Multiple_Messages(unittest.TestCase):

    def setUp(self) -> None:
        set_db_connection("sqlite","pysqlite","/:memory:")
        self.device_id = DeviceId(module_id=42, type=7, role="test_device", name="Test Device X")
        self.sdevice_id = serialized_device_id(self.device_id)

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
        send_statuses("test_company", "test_car", self.sdevice_id, messages=[self.status_example])
        statuses, code = list_statuses("test_company", "test_car", self.sdevice_id)
        self.assertEqual(len(statuses), 1)
        self.assertEqual(code, 200)
        status = statuses[0]
        self.assertEqual(status.device_id.module_id, self.status_example.device_id.module_id)
        self.assertEqual(status.device_id.type, self.status_example.device_id.type)
        self.assertEqual(status.device_id.role, self.status_example.device_id.role)
        self.assertEqual(status.payload, self.status_example.payload)

    def test_sending_empty_list_of_statuses_does_not_affect_list_of_statuses_returned_from_database(self)->None:
        send_statuses("test_company", "test_car", self.sdevice_id, messages=[self.status_example])
        statuses_before = list_statuses("test_company", "test_car", self.sdevice_id)
        send_statuses("test_company", "test_car", self.sdevice_id, messages=[])
        statuses_after = list_statuses("test_company", "test_car", self.sdevice_id)
        self.assertEqual(statuses_before, statuses_after)

    def test_sent_commands_to_available_devices(self)->None:
        sdevice_id = "42_7_test_device"
        send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            sdevice_id=sdevice_id, 
            messages=[self.status_example]
        )
        send_commands(
            company_name="test_company", 
            car_name="test_car", 
            sdevice_id=sdevice_id, 
            messages=[self.command_example]
        )
        commands, code = list_commands("test_company","test_car", sdevice_id)
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
            sdevice_id=self.sdevice_id, 
            messages=[self.status_example]
        )

        id_of_device_in_nonexistent_module = DeviceId(
            module_id=1111111, 
            type=7, 
            role="test_device", 
            name="Test Device X"
        )
        sid_of_device_in_nonexistent_module = serialized_device_id(
            id_of_device_in_nonexistent_module
        )
        command_of_device_in_nonexistent_module = Message(
            timestamp = 124879465,
            device_id=id_of_device_in_nonexistent_module, 
            payload=self.command_example.payload
        )

        response, code = send_commands(
            company_name="test_company", 
            car_name="test_car", 
            sdevice_id=sid_of_device_in_nonexistent_module, 
            messages=[command_of_device_in_nonexistent_module]
        )
        self.assertEqual(code, 404)

        response, code = send_commands(
            company_name="test_company", 
            car_name="nonexistent_car", 
            sdevice_id=self.sdevice_id, 
            messages=[self.command_example]
        )
        self.assertEqual(code, 404)

        response, code = send_commands(
            company_name="nonexistent_company", 
            car_name="test_car", 
            sdevice_id=self.sdevice_id, 
            messages=[self.command_example]
        )
        self.assertEqual(code, 404)

    def test_sending_empty_list_of_commands_does_not_affect_list_of_commands_returned_from_database(self)->None:
        send_commands("test_company", "test_car", self.sdevice_id, messages=[self.command_example])
        commands_before = list_commands("test_company", "test_car", self.sdevice_id)

        send_commands("test_company", "test_car", self.sdevice_id, messages=[])
        commands_after = list_commands("test_company", "test_car", self.sdevice_id)
        self.assertEqual(commands_before, commands_after)

    def test_sending_commands_sent_to_nonexistent_device_returns_code_404(self)->None:
        not_connected_device_id = "42_7_test_device"
        response = send_commands(
            company_name="test_company", 
            car_name="test_car", 
            sdevice_id=not_connected_device_id, 
            messages=[self.command_example]
        )
        self.assertEqual(response[1], 404)


from unittest.mock import patch
class Test_Statuses_In_Time(unittest.TestCase):

    COMPANY_1_NAME = "company_1"
    CAR_A_NAME = "car_A"
    CAR_B_NAME = "car_B"

    def setUp(self) -> None:
        set_db_connection("sqlite", "pysqlite", "/:memory:")
        self.sdevice_id = "2_5_test_device"

    def test_by_default_only_the_NEWEST_STATUS_is_returned_and_if_all_is_specified_all_statuses_are_returned(self):
        payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        
        message_1 = Message(timestamp=10, device_id=device_id, payload = payload)
        message_2 = Message(timestamp=20, device_id=device_id, payload = payload)
        message_3 = Message(timestamp=37, device_id=device_id, payload = payload)
        args = self.COMPANY_1_NAME, self.CAR_A_NAME, self.sdevice_id

        send_statuses(*args, messages=[message_1])
        send_statuses(*args, messages=[message_2])
        send_statuses(*args, messages=[message_3])

        statuses, code = list_statuses(*args)
        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[-1].timestamp, 37)

        # any value passed as 'all' attribute makes the list_statuses to return all the statuses
        statuses, code = list_statuses(*args, all_available="")
        self.assertEqual(len(statuses), 3)
        self.assertEqual(statuses[0].timestamp, 10)
        self.assertEqual(statuses[1].timestamp, 20)
        self.assertEqual(statuses[2].timestamp, 37)

        statuses, code = list_statuses(*args, since=20)
        self.assertEqual(len(statuses), 2)
        self.assertEqual(statuses[0].timestamp, 20)
        self.assertEqual(statuses[1].timestamp, 37)
    
        statuses, code = list_statuses(*args, since=38)
        self.assertEqual(len(statuses), 0)


    def test_by_default_only_the_OLDEST_COMMAND_is_returned(self):
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        sdevice = serialized_device_id(device_id)
        status_payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        command_payload = Payload(message_type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"message":"Beep"})
        
        status = Message(timestamp=10, device_id=device_id, payload=status_payload)
        command_1 = Message(timestamp=20, device_id=device_id, payload=command_payload)
        command_2 = Message(timestamp=30, device_id=device_id, payload=command_payload)
        command_3 = Message(timestamp=45, device_id=device_id, payload=command_payload)

        args = self.COMPANY_1_NAME, self.CAR_A_NAME, sdevice

        send_statuses(*args, [status])
        send_commands(*args, [command_1])
        send_commands(*args, [command_2])
        send_commands(*args, [command_3])

        commands, code = list_commands(*args)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].timestamp, 20)

        commands, code = list_commands(*args, all_available="")
        self.assertEqual(len(commands), 3)
        self.assertEqual(commands[0].timestamp, 20)
        self.assertEqual(commands[1].timestamp, 30)
        self.assertEqual(commands[2].timestamp, 45)

        commands, code = list_commands(*args, until=30)
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].timestamp, 20)
        self.assertEqual(commands[1].timestamp, 30)

        commands, code = list_commands(*args, until=5)
        self.assertEqual(len(commands), 0)


from database.database_controller import remove_old_messages
from database.database_controller import future_command_warning, MessageBase

class Test_Cleaning_Up_Commands(unittest.TestCase):

    COMPANY_1_NAME = "company_1"
    CAR_A_NAME = "car_A"
    CAR_B_NAME = "car_B"
    DATA_RETENTION_PERIOD = MessageBase.data_retention_period_ms


    def setUp(self) -> None:
        set_db_connection("sqlite", "pysqlite", "/:memory:")
        clear_device_ids()

        self.device_id = DeviceId(module_id=42, type=5, role="left_light", name="Left light")
        self.status_payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is conected"})
        self.command_payload = Payload(message_type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"message":"Beep"})
        
        sdevice_id = serialized_device_id(self.device_id)
        self.args = self.COMPANY_1_NAME, self.CAR_A_NAME, sdevice_id


    @patch('database.time._time_in_ms')
    def test_cleaning_up_commands(self, mock_timestamp):
        status = Message(timestamp=0, device_id=self.device_id, payload=self.status_payload)
        command_1 = Message(timestamp=10, device_id=self.device_id, payload=self.command_payload)
        command_2 = Message(timestamp=20, device_id=self.device_id, payload=self.command_payload)

        send_statuses(*self.args, [status])
        send_commands(*self.args, [command_1])
        send_commands(*self.args, [command_2])

        self.assertEqual(len(list_statuses(*self.args, all_available="")[0]), 1)
        self.assertEqual(len(list_commands(*self.args, all_available="")[0]), 2)

        mock_timestamp.return_value = self.DATA_RETENTION_PERIOD+20
        remove_old_messages(mock_timestamp.return_value)

        self.assertEqual(len(list_statuses(*self.args, all_available="")[0]), 0)
        self.assertEqual(len(list_commands(*self.args, all_available="")[0]), 0)
        
        mock_timestamp.return_value += 5 
        
        # the following status is considered to be the FIRST status for given device and after sending it, 
        # all commands previously sent to this device have to be removed
        send_statuses(*self.args, [status])
        self.assertEqual(len(list_statuses(*self.args, all_available="")[0]), 1)
        self.assertEqual(len(list_commands(*self.args, all_available="")[0]), 0)


    @patch('database.time._time_in_ms')
    def test_cleaning_up_command_with_newer_timestamp_relative_to_the_first_status_raises_warning(self, mock_timestamp):
        status = Message(timestamp=0, device_id=self.device_id, payload=self.status_payload)
        new_first_status = Message(timestamp=self.DATA_RETENTION_PERIOD + 50, device_id=self.device_id, payload=self.status_payload)
        command_1 = Message(timestamp=self.DATA_RETENTION_PERIOD+30, device_id=self.device_id, payload=self.command_payload)
        # the following timestamp is invalid as it is set to the future relative to the next (FIRST) status
        command_2 = Message(timestamp=self.DATA_RETENTION_PERIOD+100, device_id=self.device_id, payload=self.command_payload)

        send_statuses(*self.args, [status])

        self.assertEqual(
            available_devices(self.COMPANY_1_NAME, self.CAR_A_NAME)[0], 
            [Module(module_id=42, device_list=[self.device_id])]
        )
        self.assertEqual(available_cars(),[Car(self.COMPANY_1_NAME, self.CAR_A_NAME)])

        send_commands(*self.args, [command_1])
        send_commands(*self.args, [command_2])

        remove_old_messages(self.DATA_RETENTION_PERIOD + 10)

        self.assertEqual(len(list_statuses(*self.args, all_available="")[0]), 0)
        # The device is considered to be disconnected and all commands sent to it are then 
        # considered to be removed.
        self.assertEqual(len(list_commands(*self.args, all_available="")[0]), 0)

        self.assertEqual(
            available_devices(self.COMPANY_1_NAME, self.CAR_A_NAME), 
            ([], 404)
        )
        self.assertEqual(available_cars(), [])

        warnings, code = send_statuses(*self.args, [new_first_status])
        self.assertEqual(len(list_statuses(*self.args, all_available="")[0]), 1)
        self.assertEqual(len(list_commands(*self.args, all_available="")[0]), 0) 

        assert(type(warnings) is str)
        for warning in future_command_warning(
                    timestamp=self.DATA_RETENTION_PERIOD + 100,
                    company_name=self.COMPANY_1_NAME,
                    car_name=self.CAR_A_NAME,
                    serialized_device_id= serialized_device_id(self.device_id),
                    payload_data=command_2.payload.data
                ):
            self.assertIn(warning, warnings)


class Test_Listing_Commands_And_Statuses_Of_Nonexistent_Cars(unittest.TestCase):

    def setUp(self) -> None:
        set_db_connection("sqlite", "pysqlite", "/:memory:")
        device_id = DeviceId(module_id=15, type=3, role="available_device", name="Available device")
        sdevice_id = serialized_device_id(device_id)
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
            sdevice_id=sdevice_id, 
            messages=[status]
        )

    def test_listing_statuses_of_nonexistent_company_returns_code_404(self):
        self.assertEqual(list_statuses("nonexistent_company", "a_car", "7_4_role"), ([], 404))

    def test_listing_commands_of_nonexistent_company_returns_code_404(self):
        self.assertEqual(list_commands("nonexistent_company", "a_car", "7_4_role"), ([], 404))

    def test_listing_statuses_of_nonexistent_car(self):
        self.assertEqual(list_statuses("a_company", "nonexistent_car", "7_4_role"), ([], 404))

    def test_listing_commands_of_nonexistent_car(self):
        self.assertEqual(list_commands("a_company", "nonexistent_car", "7_4_role"), ([], 404))




class Test_Correspondence_Between_Payload_Type_And_Send_Command_And_Send_Status_Methods(unittest.TestCase):

    def test_send_statuses_accepts_only_statuses(self):
        payload = Payload(message_type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"message":"Beep"})
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        command = Message(timestamp=10, device_id=device_id, payload=payload)
        _, code = send_statuses("test_company", "test_car", "7_4_role", [command])
        self.assertEqual(code, 500)

    def test_send_commands_accepts_only_commands(self):
        payload = Payload(message_type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"message":"Device is running"})
        device_id = DeviceId(module_id=2, type=5, role="test_device", name="Test Device")
        status = Message(timestamp=10, device_id=device_id, payload=payload)
        _, code = send_commands("test_company", "test_car", "7_4_role", [status])
        self.assertEqual(code, 500)


from sqlalchemy import insert
from database.connection import get_connection_source
from database.database_controller import MessageBase, get_available_devices_from_database
class Test_Store_Available_Device_Ids_After_Connecting_To_Database_Already_Containing_Data(unittest.TestCase):

    def setUp(self) -> None:
        clear_device_ids()

    def test_list_available_cars(self):
        set_db_connection("sqlite", "pysqlite", "/:memory:")
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

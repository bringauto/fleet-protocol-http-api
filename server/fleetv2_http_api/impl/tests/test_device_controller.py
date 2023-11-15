import sys
sys.path.append("server")


import unittest
from database.database_controller import set_connection_source
from fleetv2_http_api.impl.device_controller import available_devices, available_cars
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Payload

from fleetv2_http_api.impl.device_controller import send_statuses, send_commands, list_statuses, list_commands
from fleetv2_http_api.impl.device_controller import _serialized_device_id, _serialized_car_info
from database.device_ids import clear_device_ids


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
        set_connection_source("sqlite","pysqlite","/:memory:")
        self.payload_example = Payload(
            type=0, 
            encoding="JSON", 
            data={"message":"Device is running"}
        )
        clear_device_ids()

    def test_device_is_considered_available_if_at_least_one_status_is_in_the_database(self):
        device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Test Device 1")
        self.assertEqual(
            available_devices("test_company", "test_car"), 
            ([], 404)
        )
        send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            device_id=device_id, 
            payload=[self.payload_example]
        )
        # assuming that the status is still in the database
        self.assertListEqual(
            available_devices("test_company", "test_car"), 
            [_serialized_device_id(device_id)]
        )
        self.assertEqual(
            available_devices("other_company", "some_car"), 
            ([], 404)
        )
    
    def test_car_is_considered_available_if_at_least_one_of_its_devices_are_available(self):
        self.assertListEqual(available_cars(), [])
        device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Test Device 1")
        response, code = send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            device_id=device_id, 
            payload=[self.payload_example]
        )
        self.assertEqual(code, 200)
        self.assertListEqual(available_cars(), [_serialized_car_info("test_company", "test_car")])


class Test_Sending_And_Listing_Messages(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source("sqlite","pysqlite","/:memory:")
        self.status_payload_example = Payload(
            type=0, 
            encoding="JSON", 
            data={"message":"Device is running"}
        )
        self.command_payload_example = Payload(
            type=1, 
            encoding="JSON", 
            data={"message":"Beep"}
        )
        clear_device_ids()

    def test_listing_sent_statuses(self)->None:
        device_id = DeviceId(module_id=42, type=7, role="testing_device_x", name="Testing Device")
        send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            device_id=device_id, 
            payload=[self.status_payload_example]
        )
        statuses, code = list_statuses("test_company", "test_car", device_id)
        self.assertEqual(len(statuses), 1)
        self.assertEqual(code, 200)
        self.assertEqual(statuses[0].payload, self.status_payload_example)

    def test_sent_commands(self)->None:
        device_id = DeviceId(module_id=42, type=7, role="testing_device_x", name="Testing Device")
        send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            device_id=device_id, 
            payload=[self.status_payload_example]
        )
        send_commands(
            company_name="test_company", 
            car_name="test_car", 
            device_id=device_id, 
            payload=[self.command_payload_example]
        )
        commands, code = list_commands("test_company","test_car", device_id)
        self.assertEqual(code, 200)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].payload, self.command_payload_example)

    def test_sending_commands_sent_to_nonexistent_device_returns_code_404(self)->None:
        not_connected_device_id = DeviceId(module_id=42, type=7, role="test_device_x", name="Not_Connected_Device")
        response = send_commands(
            company_name="test_company", 
            car_name="test_car", 
            device_id=not_connected_device_id, 
            payload=[self.command_payload_example]
        )
        self.assertEqual(response[1], 404)


from unittest.mock import patch
class Test_Statuses_In_Time(unittest.TestCase):

    COMPANY_1_NAME = "company_1"
    CAR_A_NAME = "car_A"
    CAR_B_NAME = "car_B"

    def setUp(self) -> None:
        set_connection_source("sqlite", "pysqlite", "/:memory:")
        self.status_type = 0
        self.command_type = 1
        self.device_id = DeviceId(module_id=42, type=5, role="left light", name="Light")

    @patch('fleetv2_http_api.impl.device_controller.timestamp')
    def test_by_default_only_the_NEWEST_STATUS_is_returned_and_if_all_is_specified_all_statuses_are_returned(self, mock_timestamp):
        payload = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        args = self.COMPANY_1_NAME, self.CAR_A_NAME, self.device_id

        mock_timestamp.return_value = 10
        send_statuses(*args, [payload])
        mock_timestamp.return_value = 20
        send_statuses(*args, [payload])
        mock_timestamp.return_value = 37
        send_statuses(*args, [payload])

        statuses, code = list_statuses(*args)
        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0].timestamp, 37)

        # any value passed as 'all' attribute makes the list_statuses to return all the statuses
        statuses, code = list_statuses(*args, all=True)
        self.assertEqual(len(statuses), 3)
        self.assertEqual(statuses[0].timestamp, 10)
        self.assertEqual(statuses[1].timestamp, 20)
        self.assertEqual(statuses[2].timestamp, 37)

        statuses, code = list_statuses(*args, since=20)
        self.assertEqual(len(statuses), 2)
        self.assertEqual(statuses[0].timestamp, 10)
        self.assertEqual(statuses[1].timestamp, 20)
    
        statuses, code = list_statuses(*args, since=5)
        self.assertEqual(len(statuses), 0)


    @patch('fleetv2_http_api.impl.device_controller.timestamp')
    def test_by_default_only_the_OLDEST_COMMAND_is_returned(self, mock_timestamp):
        status_payload = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        command_payload = Payload(type=1, encoding="JSON", data={"message":"Beep"})

        args = self.COMPANY_1_NAME, self.CAR_A_NAME, self.device_id

        mock_timestamp.return_value = 10
        send_statuses(*args, [status_payload])
        mock_timestamp.return_value += 10
        send_commands(*args, [command_payload])
        mock_timestamp.return_value += 10
        send_commands(*args, [command_payload])
        mock_timestamp.return_value += 15
        send_commands(*args, [command_payload])

        commands, code = list_commands(*args)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].timestamp, 20)

        commands, code = list_commands(*args, all=True)
        self.assertEqual(len(commands), 3)
        self.assertEqual(commands[0].timestamp, 20)
        self.assertEqual(commands[1].timestamp, 30)
        self.assertEqual(commands[2].timestamp, 45)

        commands, code = list_commands(*args, since=30)
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0].timestamp, 20)
        self.assertEqual(commands[1].timestamp, 30)

        commands, code = list_commands(*args, since=5)
        self.assertEqual(len(commands), 0)


from database.time import DATA_RETENTION_PERIOD
class Test_Cleaning_Up_Commands(unittest.TestCase):

    COMPANY_1_NAME = "company_1"
    CAR_A_NAME = "car_A"
    CAR_B_NAME = "car_B"


    def setUp(self) -> None:
        set_connection_source("sqlite", "pysqlite", "/:memory:")
        self.status_type = 0
        self.command_type = 1
        self.device_id = DeviceId(module_id=42, type=5, role="left light", name="Light")
        # clear_device_ids()


    @patch('fleetv2_http_api.impl.device_controller.timestamp')
    def test_cleaning_up_commands(self, mock_timestamp):
        status_payload = Payload(type=0, encoding="JSON", data={"message":"Device is conected"})
        command_payload = Payload(type=1, encoding="JSON", data={"message":"Beep"})
        args = self.COMPANY_1_NAME, self.CAR_A_NAME, self.device_id

        mock_timestamp.return_value = 0
        send_statuses(*args, [status_payload])
        mock_timestamp.return_value += 10
        send_commands(*args, [command_payload])

        commands, code = list_commands(*args, all=True)
        self.assertEqual(len(commands), 1)

        mock_timestamp.return_value += DATA_RETENTION_PERIOD
        


# from fleetv2_http_api.impl.device_controller import _count_currently_stored_messages
# class Test_Records_Older_Than_One_Hour_Are_Automatically_Removed(unittest.TestCase):

#     def setUp(self) -> None:
#         set_connection_source("sqlite", "pysqlite", "/:memory:")
#         self.device_id = DeviceId(module_id=42, type=4, role="light", name="Left light")
#         self.status_payload = Payload(type=0, encoding="JSON", data={})

#     @patch('fleetv2_http_api.impl.device_controller.timestamp')
#     def test_statuses_older_than_one_hour_are_deleted_when_listing_statuses(self, mock_timestamp):
#         STATUS_1_TIMESTAMP = 1000000
#         STATUS_2_TIMESTAMP = 1000000 + 1000
#         SMALLER_THAN_HOUR = 12300
#         ONE_HOUR = 3600000

#         status_1 = Message(timestamp=STATUS_1_TIMESTAMP, id=self.device_id, payload=self.status_payload)
#         status_2 = Message(timestamp=STATUS_2_TIMESTAMP, id=self.device_id, payload=self.status_payload)
#         _add_msg(status_1, status_2)

#         mock_timestamp.return_value = STATUS_1_TIMESTAMP + SMALLER_THAN_HOUR
#         self.assertListEqual(list_statuses(self.device_id, all=True), [status_1, status_2])

#         mock_timestamp.return_value = STATUS_1_TIMESTAMP + ONE_HOUR
#         self.assertListEqual(list_statuses(self.device_id, all=True), [status_1, status_2])
    
#         mock_timestamp.return_value = STATUS_1_TIMESTAMP + ONE_HOUR + 1
#         self.assertListEqual(list_statuses(self.device_id, all=True), [status_2])

#         mock_timestamp.return_value = STATUS_2_TIMESTAMP + ONE_HOUR + 1
#         self.assertListEqual(list_statuses(self.device_id, all=True), [])

#     @patch('fleetv2_http_api.impl.device_controller.timestamp')
#     def test_statuses_older_than_one_hour_are_deleted_when_sending_statuses(self, mock_timestamp):
#         ONE_HOUR = 3600000
#         STATUS_1_TIMESTAMP = 1000000
#         STATUS_2_TIMESTAMP = 1000000 + ONE_HOUR + 1

#         mock_timestamp.return_value = STATUS_1_TIMESTAMP
#         send_statuses(self.device_id, [self.status_payload])
#         self.assertEqual(_count_currently_stored_messages(), 1)
#         mock_timestamp.return_value = STATUS_2_TIMESTAMP
        
#         send_statuses(self.device_id, [self.status_payload])
#         self.assertEqual(_count_currently_stored_messages(), 1)
#         self.assertEqual(list_statuses(self.device_id, all=True)[0].timestamp, STATUS_2_TIMESTAMP)


if __name__=="__main__":
    unittest.main()

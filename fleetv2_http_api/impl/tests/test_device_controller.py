import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.db import set_connection_source
from fleetv2_http_api.impl.device_controller import _add_msg, available_devices
from fleetv2_http_api.models.device import Message, Payload, DeviceId



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


class Test_Listing_Available_Devices(unittest.TestCase):
    
    def setUp(self) -> None:
        set_connection_source("sqlite","pysqlite","/:memory:")
        self.payload_example = Payload(
            type=0, 
            encoding="JSON", 
            data={"message":"Device is running"}
        )

    def test_adding_and_retrieve_single_device(self):
        device_id = DeviceId(42, 2, "light", "Left light")
        msg = Message(123456789, device_id, self.payload_example)
        _add_msg(msg)
        devices = available_devices()
        self.assertEqual(devices[0], device_id)

    def test_adding_and_retrieve_multiple_devices(self):
        device_1_id = DeviceId(42, 2, "light", "Left light")
        device_2_id= DeviceId(43, 2, "light", "Right light")

        msg_1 = Message(123456789, device_1_id, self.payload_example)
        msg_2 = Message(123456789, device_2_id, self.payload_example)
        _add_msg(msg_1)
        _add_msg(msg_2)
        self.assertListEqual(available_devices(), [device_1_id, device_2_id])

    def test_adding_and_displaying_devices_in_multiple_modules(self):
        device_1_id = DeviceId(module_id=42, type=0, role="light", name="Left light")
        device_2_id = DeviceId(module_id=43, type=0, role="light", name="Right light")

        msg_1 = Message(123456789, device_1_id, self.payload_example)
        msg_2 = Message(123456789, device_2_id, self.payload_example)
        _add_msg(msg_1)
        _add_msg(msg_2)
        self.assertListEqual(available_devices(), [device_1_id, device_2_id])
        self.assertListEqual(available_devices(module_id=42), [device_1_id])
        self.assertListEqual(available_devices(module_id=43), [device_2_id])

        result_for_nonexistent_module = available_devices(module_id=-58)
        self.assertEqual(result_for_nonexistent_module, ([], 404))


from fleetv2_http_api.impl.device_controller import list_statuses, list_commands, send_commands, send_statuses
from unittest.mock import patch


class Test_Retrieving_Device_Messages(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source("sqlite", "pysqlite", "/:memory:")
        self.status_type = 0
        self.command_type = 1
        self.device_id = DeviceId(module_id=42, type=5, role="left light", name="Light")

    def test_by_default_only_the_NEWEST_STATUS_is_returned(self):
        payload = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        msg_older = Message(timestamp=123456, id=self.device_id, payload=payload)
        msg_newer = Message(timestamp=123458, id=self.device_id, payload=payload)
        _add_msg(msg_older, msg_newer)
        statuses = list_statuses(self.device_id)
        self.assertListEqual(statuses, [msg_newer])

    def test_by_default_only_the_OLDEST_COMMAND_is_returned(self):
        payload = Payload(type=1, encoding="JSON", data={"message":"Device is running"})
        msg_older = Message(timestamp=123456, id=self.device_id, payload=payload)
        msg_newer = Message(timestamp=123458, id=self.device_id, payload=payload)
        _add_msg(msg_older, msg_newer)
        statuses = list_commands(self.device_id)
        self.assertListEqual(statuses, [msg_older])

    def test_listing_device_messages(self):
        payload_1 = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        payload_2 = Payload(type=1, encoding="JSON", data={"message":"Device! Do something!"})
        msg_1 = Message(timestamp=123456, id=self.device_id, payload=payload_1)
        msg_2 = Message(timestamp=123458, id=self.device_id, payload=payload_2)
        _add_msg(msg_1, msg_2)
        statuses = list_statuses(self.device_id)
        commands = list_commands(self.device_id)
        self.assertListEqual(statuses, [msg_1])
        self.assertListEqual(commands, [msg_2])

    def test_listing_all_statuses_and_statuses_inclusively_older_than_given_timestamp(self):
        payload_1 = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        payload_2 = Payload(type=0, encoding="JSON", data={"message":"Device is still running"})
        payload_3 = Payload(type=0, encoding="JSON", data={"message":"Hooray! The device is running"})

        status_1 = Message(timestamp=123, id=self.device_id, payload=payload_1)
        status_2 = Message(timestamp=124, id=self.device_id, payload=payload_2)
        status_3 = Message(timestamp=125, id=self.device_id, payload=payload_3)

        _add_msg(status_1, status_2, status_3)
        statuses = list_statuses(self.device_id, all=True)
        self.assertListEqual(statuses, [status_1, status_2, status_3])

        statuses = list_statuses(self.device_id, since=124)
        self.assertListEqual(statuses, [status_1, status_2])

    def test_listing_all_commands_and_commands_inclusively_older_than_given_timestamp(self):
        payload_1 = Payload(type=1, encoding="JSON", data={"message":"Device is running"})
        payload_2 = Payload(type=1, encoding="JSON", data={"message":"Device is still running"})
        payload_3 = Payload(type=1, encoding="JSON", data={"message":"Hooray! The device is running"})

        cmd_1 = Message(timestamp=123, id=self.device_id, payload=payload_1)
        cmd_2 = Message(timestamp=124, id=self.device_id, payload=payload_2)
        cmd_3 = Message(timestamp=125, id=self.device_id, payload=payload_3)

        _add_msg(cmd_1, cmd_2, cmd_3)
        cmds = list_commands(self.device_id, all=True)
        self.assertListEqual(cmds, [cmd_1, cmd_2, cmd_3])
        cmds = list_commands(self.device_id, since=124)
        self.assertListEqual(cmds, [cmd_1, cmd_2])

    def test_empty_list_is_returned_when_no_message_is_available(self):
        self.assertListEqual(list_statuses(self.device_id), [])
        self.assertListEqual(list_statuses(self.device_id, all=True), [])
        self.assertListEqual(list_commands(self.device_id), [])
        self.assertListEqual(list_commands(self.device_id, all=True), [])

    def test_empty_list_is_returned_when_no_message_is_older_than_timestamp(self):
        payload_1 = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        status_1 = Message(timestamp=123, id=self.device_id, payload=payload_1)
        _add_msg(status_1)
        self.assertListEqual(list_statuses(self.device_id, since=123), [status_1])
        self.assertListEqual(list_statuses(self.device_id, since=122), [])

    def test_obtained_messages_correspond_to_device_ids_specified_when_adding_the_messages(self):
        other_device_id = DeviceId(
            module_id=self.device_id.module_id, 
            type=self.device_id.type, 
            role="right light", 
            name=self.device_id.name
        )

        payload = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        status_1 = Message(timestamp=123, id=self.device_id, payload=payload)
        status_2 = Message(timestamp=123, id=other_device_id, payload=payload)
        _add_msg(status_1, status_2)
        self.assertListEqual(list_statuses(self.device_id, all=True), [status_1])
        self.assertListEqual(list_statuses(other_device_id, all=True), [status_2])


class Test_Sending_Device_Messages(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source("sqlite", "pysqlite", "/:memory:")
        self.status_type = 0
        self.command_type = 1

    @patch('fleetv2_http_api.impl.device_controller.timestamp')
    def test_sending_and_retrieving_device_messages(self, mock_timestamp):
        device_id = DeviceId(module_id=42, type=4, role="light", name="Left light")
        status_1 = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        status_2 = Payload(type=0, encoding="JSON", data={"message":"Device is still running"})
        command_1 = Payload(type=1, encoding="JSON", data={"message":"Stop"})
        
        mock_timestamp.side_effect = [123456, 123457, 123459]

        send_statuses(device_id, payload=[status_1, status_2])
        send_commands(device_id, payload=[command_1])

        statuses = list_statuses(device_id, all=True)
        commands = list_commands(device_id, all=True)

        self.assertEqual(statuses[0].payload, status_1)
        self.assertEqual(statuses[1].payload, status_2)
        self.assertEqual(commands[0].payload, command_1)

    def test_commands_sent_to_device_at_once_share_common_timestamp(self):
        device_id = DeviceId(module_id=42, type=4, role="light", name="Left light")
        cmd_1 = Payload(type=1, encoding="JSON", data={})
        cmd_2 = Payload(type=1, encoding="JSON", data={})
        send_commands(device_id, payload=[cmd_1, cmd_2])
        stored_commands = list_commands(device_id, all=True)

        self.assertEqual(stored_commands[0].timestamp, stored_commands[1].timestamp)

    def test_statuses_sent_to_device_at_once_share_common_timestamp(self):
        device_id = DeviceId(module_id=42, type=4, role="light", name="Left light")
        stat_1 = Payload(type=0, encoding="JSON", data={})
        stat_2 = Payload(type=0, encoding="JSON", data={})
        send_statuses(device_id, payload=[stat_1, stat_2])
        stored_statuses = list_statuses(device_id, all=True)

        self.assertEqual(stored_statuses[0].timestamp, stored_statuses[1].timestamp)

    


if __name__=="__main__":
    unittest.main()
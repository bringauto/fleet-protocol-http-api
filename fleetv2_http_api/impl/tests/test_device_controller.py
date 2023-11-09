import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.db import set_connection_source
from fleetv2_http_api.impl.device_controller import add_msg, devices_available
from fleetv2_http_api.models.device import Message, Payload, DeviceId


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
        add_msg(msg)
        devices = devices_available()
        self.assertEqual(devices[0], device_id)

    def test_adding_and_retrieve_multiple_devices(self):
        device_1_id = DeviceId(42, 2, "light", "Left light")
        device_2_id= DeviceId(43, 2, "light", "Right light")

        msg_1 = Message(123456789, device_1_id, self.payload_example)
        msg_2 = Message(123456789, device_2_id, self.payload_example)
        add_msg(msg_1)
        add_msg(msg_2)
        self.assertListEqual(devices_available(), [device_1_id, device_2_id])

    def test_adding_and_displaying_devices_in_multiuple_modules(self):
        device_1_id = DeviceId(module_id=42, type=0, role="light", name="Left light")
        device_2_id = DeviceId(module_id=43, type=0, role="light", name="Right light")

        msg_1 = Message(123456789, device_1_id, self.payload_example)
        msg_2 = Message(123456789, device_2_id, self.payload_example)
        add_msg(msg_1)
        add_msg(msg_2)
        self.assertListEqual(devices_available(), [device_1_id, device_2_id])
        self.assertListEqual(devices_available(module_id=42), [device_1_id])
        self.assertListEqual(devices_available(module_id=43), [device_2_id])

        result_for_nonexistent_module = devices_available(module_id=-58)
        self.assertEqual(result_for_nonexistent_module, ([], 404))


from fleetv2_http_api.impl.device_controller import list_statuses, list_commands
class Test_Handling_Device_Messages(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source("sqlite", "pysqlite", "/:memory:")
        self.status_type = 0
        self.command_type = 1

    def test_listing_device_messages(self):
        device_id = DeviceId(module_id=42, type=self.status_type, role="light", name="Left light")
        payload_1 = Payload(type=0, encoding="JSON", data={"message":"Device is running"})
        payload_2 = Payload(type=0, encoding="JSON", data={"message":"Device is fine"})
        payload_3 = Payload(type=1, encoding="JSON", data={"message":"Device! Do something!"})
        msg_1 = Message(timestamp=123456, id=device_id, payload=payload_1)
        msg_2 = Message(timestamp=123457, id=device_id, payload=payload_2)
        msg_3 = Message(timestamp=123458, id=device_id, payload=payload_3)
        add_msg(msg_1, msg_2, msg_3)
        statuses = list_statuses(device_id)
        commands = list_commands(device_id)
        self.assertListEqual(statuses, [msg_1, msg_2])
        self.assertListEqual(commands, [msg_3])


if __name__=="__main__":
    unittest.main()
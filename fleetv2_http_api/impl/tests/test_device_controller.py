import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.db import set_connection_source
from fleetv2_http_api.impl.device_controller import add_device, devices_available
from fleetv2_http_api.models.device import Device, Payload, DeviceId


class Test_Listing_Available_Devices(unittest.TestCase):
    
    def setUp(self) -> None:
        set_connection_source("sqlite","pysqlite","/:memory:")
        self.payload_example = Payload(type=2, encoding="JSON", data={"message":"Device is running"})

    def test_adding_and_retrieve_single_device(self):
        device_id = DeviceId(42, 2, "light", "Left light")
        device = Device(123456789, device_id, self.payload_example)
        add_device(device)
        devices = devices_available()
        self.assertEqual(devices[0].id, device_id)
        self.assertEqual(devices[0].payload.type, 2)
        self.assertEqual(devices[0].payload.data["message"], "Device is running") # type: ignore

    def test_adding_and_retrieve_multiple_devices(self):
        device_1_id = DeviceId(42, 2, "light", "Left light")
        device_2_id= DeviceId(43, 2, "light", "Right light")

        device_1 = Device(123456789, device_1_id, self.payload_example)
        device_2 = Device(123456789, device_2_id, self.payload_example)
        add_device(device_1)
        add_device(device_2)
        self.assertListEqual(devices_available(), [device_1, device_2])

    def test_adding_and_displaying_devices_in_multiuple_modules(self):
        device_1_id = DeviceId(module_id=42, type=2, role="light", name="Left light")
        device_2_id = DeviceId(module_id=43, type=2, role="light", name="Right light")

        device_1 = Device(123456789, device_1_id, self.payload_example)
        device_2 = Device(123456789, device_2_id, self.payload_example)
        add_device(device_1)
        add_device(device_2)
        self.assertListEqual(devices_available(), [device_1, device_2])
        self.assertListEqual(devices_available(module_id=42), [device_1])
        self.assertListEqual(devices_available(module_id=43), [device_2])

        result_for_nonexistent_module = devices_available(module_id=-58)
        self.assertEqual(result_for_nonexistent_module, ([], 404))


if __name__=="__main__":
    unittest.main()
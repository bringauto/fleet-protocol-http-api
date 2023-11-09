import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.db import set_connection_source
from fleetv2_http_api.impl.device_controller import add_device, devices_available
from fleetv2_http_api.models.device import Device, Payload


class Test_Listing_Available_Devices(unittest.TestCase):
    
    def setUp(self) -> None:
        set_connection_source("sqlite","pysqlite","/:memory:")
        self.car_name = "mixi7895"
        self.company_name = "bringauto"

    def test_adding_and_retrieve_single_device(self):
        payload = Payload(type=2, encoding="JSON", data={"message":"Device XY is running"})
        device = Device(timestamp=123456789, id=42, payload=payload)
        add_device(self.company_name, self.car_name, device)
        devices = devices_available(
            company_name=self.company_name, 
            car_name=self.car_name,
            module_id=1
        )
        self.assertEqual(devices[0].id, 42)
        self.assertEqual(devices[0].payload.type, 2)
        self.assertEqual(devices[0].payload.data["message"], "Device XY is running")


if __name__=="__main__":
    unittest.main()
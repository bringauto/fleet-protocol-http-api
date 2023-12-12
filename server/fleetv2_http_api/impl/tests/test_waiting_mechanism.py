import sys
sys.path.append("server")


import unittest
from database.device_ids import clear_device_ids, serialized_device_id
from database.database_controller import set_db_connection
from fleetv2_http_api.impl.controllers import (
    send_statuses, 
    list_statuses, 
)
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Payload, Message
from fleetv2_http_api.models.module import Module
from fleetv2_http_api.models.car import Car


import fleetv2_http_api.impl.wait as wait


class Test_Listing_Statuses(unittest.TestCase):

    def setUp(self) -> None:
        set_db_connection("sqlite","pysqlite","/:memory:")
        clear_device_ids()
        payload_example = Payload(
            message_type='STATUS', 
            encoding='JSON', 
            data={"message":"Device is running"}
        )
        self.device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Left light")
        self.sdevice_id = serialized_device_id(self.device_id)
        self.status_example = Message(
            timestamp=123456789,
            device_id=self.device_id,
            payload=payload_example
        )

    def test_return_statuses_immediatelly_if_some_are_avaialable(self):
        send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            sdevice_id=self.sdevice_id, 
            messages=[self.status_example]
        )
        statuses, code = list_statuses(company_name="test_company", car_name="test_car", sdevice_id=self.sdevice_id, wait="")
        self.assertEqual(len(statuses), 1)


class Test_Creating_Wait_Objects(unittest.TestCase):

    def setUp(self) -> None:
        self.mg = wait.Wait_Manager()

    def test_creating_new_wait_obj(self):
        self.mg.wait_for("test_company", "test_car", "id_xyz")
        self.assertTrue(self.mg.is_waiting("test_company", "test_car", "id_xyz"))
        self.assertFalse(self.mg.is_waiting("test_company", "other_car", "id_ABC"))

        self.mg.wait_for("test_company", "other_car", "id_ABC")
        self.assertTrue(self.mg.is_waiting("test_company", "other_car", "id_ABC"))

    def test_stop_waiting(self)->None:
        self.mg.wait_for("test_company", "test_car", "id_xyz")
        self.assertTrue(self.mg.is_waiting("test_company", "test_car", "id_xyz"))
        self.mg.stop_waiting("test_company", "test_car", "id_xyz")
        self.assertFalse(self.mg.is_waiting("test_company", "test_car", "id_xyz"))

    


if __name__=="__main__": 
    unittest.main()

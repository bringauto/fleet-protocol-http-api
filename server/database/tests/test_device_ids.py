import sys
sys.path.append("server")


import unittest
from database.device_ids import (
    device_ids, 
    clean_up_disconnected_cars_and_modules, 
    clear_device_ids,
    store_device_id_if_new,
    remove_device_id
)


class TestDeviceIds(unittest.TestCase):
    
    def test_cleaning_up_cars_without_any_device_ids(self):
        clear_device_ids()
        store_device_id_if_new("company1", "car1", 1, "device1")
        store_device_id_if_new("company1", "car2", 1, "deviceX")
        self.assertEqual(list(device_ids()["company1"].keys()), ["car1", "car2"])
        remove_device_id("company1", "car1", 1, "device1")
        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(device_ids(), {"company1":{"car2":{1:["deviceX"]}}})

    def test_cleaning_up_modules_without_any_device_ids(self):
        clear_device_ids()
        store_device_id_if_new("company1", "car1", 1, "device1")
        store_device_id_if_new("company1", "car1", 2, "deviceX")
        remove_device_id("company1", "car1", 2, "deviceX")
        
        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(device_ids(), {"company1":{"car1":{1:["device1"]}}})

    def test_cleaning_up_companies_without_any_cars(self):
        clear_device_ids()
        store_device_id_if_new("company1", "car1", 1, "device1")
        store_device_id_if_new("company2", "car1", 1, "deviceX")
        store_device_id_if_new("company3", "carA", 1, "device_0123")

        remove_device_id("company2", "car1", 1, "deviceX")
        clean_up_disconnected_cars_and_modules()
        self.assertListEqual(list(device_ids().keys()), ["company1", "company3"])

    def test_cleaning_up_empty_device_ids_dict_has_no_effect(self):
        clear_device_ids()
        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(device_ids(), {})


if __name__ == '__main__':
    unittest.main()
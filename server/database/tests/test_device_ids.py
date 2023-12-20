import sys
sys.path.append("server")


import unittest
from database.device_ids import (
    device_ids,
    clean_up_disconnected_cars_and_modules,
    clear_device_ids,
    store_device_id_if_new,
    remove_device_id,
    serialized_device_id
)


from fleetv2_http_api.models.device_id import DeviceId
class TestDeviceIds(unittest.TestCase):

    def setUp(self):
        self.device_1_id = DeviceId(module_id=45, type=2, role="role1", name="device1")
        self.device_x_id = DeviceId(module_id=48, type=7, role="role_x", name="device X")
        self.device_123_id = DeviceId(module_id=45, type=9, role="role_123", name="device 123")
        self.device_456_id = DeviceId(module_id=58, type=9, role="role_456", name="device 456")
        self.maxDiff = None

    def test_cleaning_up_cars_without_any_device_ids(self):
        clear_device_ids()
        store_device_id_if_new("company1", "car1", self.device_1_id)
        store_device_id_if_new("company1", "car2", self.device_x_id)
        self.assertEqual(list(device_ids()["company1"].keys()), ["car1", "car2"])
        remove_device_id("company1", "car1", self.device_1_id)
        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(
            device_ids(),
            {"company1":{"car2":{
                48:{
                    "48_7_role_x":self.device_x_id
                }
            }}}
        )

    def test_cleaning_up_modules_without_any_device_ids(self):
        clear_device_ids()
        store_device_id_if_new("company1", "car1", self.device_1_id)
        store_device_id_if_new("company1", "car1", self.device_x_id)
        remove_device_id("company1", "car1", self.device_x_id)

        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(
            device_ids(),
            {"company1":{"car1":{
                45:{
                    "45_2_role1":self.device_1_id
                },
                }
            }}
        )

    def test_cleaning_up_companies_without_any_cars(self):
        clear_device_ids()
        store_device_id_if_new("company1", "car1", self.device_1_id)
        store_device_id_if_new("company2", "car1", self.device_x_id)
        store_device_id_if_new("company3", "carA", self.device_123_id)
        store_device_id_if_new("company3", "carB", self.device_456_id)

        store_device_id_if_new("company1", "car1", self.device_1_id)

        remove_device_id("company2", "car1", self.device_x_id)
        clean_up_disconnected_cars_and_modules()
        self.assertListEqual(list(device_ids().keys()), ["company1", "company3"])

        remove_device_id("company1", "car1", serialized_device_id(self.device_1_id))
        clean_up_disconnected_cars_and_modules()
        self.assertListEqual(list(device_ids().keys()), ["company3"])

    def test_cleaning_up_empty_device_ids_dict_has_no_effect(self):
        clear_device_ids()
        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(device_ids(), {})


if __name__ == '__main__':
    unittest.main()
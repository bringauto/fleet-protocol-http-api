import sys

sys.path.append("server")
import unittest

from fleetv2_http_api.models.device_id import DeviceId   # type: ignore
from database.device_ids import (  # type: ignore
    add_car,
    add_device,
    connected_cars,
    clean_up_disconnected_cars_and_modules,
    clear_connected_cars,
    remove_connected_device,
    serialized_device_id,
    ConnectedCar,
    ConnectedModule
)


class TestDeviceIds(unittest.TestCase):
    def setUp(self):
        self.device_1_id = DeviceId(module_id=45, type=2, role="role1", name="device1")
        self.device_x_id = DeviceId(module_id=48, type=7, role="role_x", name="device X")
        self.device_123_id = DeviceId(module_id=45, type=9, role="role_123", name="device 123")
        self.device_456_id = DeviceId(module_id=58, type=9, role="role_456", name="device 456")
        self.maxDiff = None

    def test_cleaning_up_cars_without_any_device_ids(self):
        clear_connected_cars()
        add_car("company1", "car1",  timestamp=0)
        add_car("company1", "car2",  timestamp=0)
        add_device("company1", "car1", self.device_1_id, timestamp=0)
        add_device("company1", "car2", self.device_x_id, timestamp=0)
        self.assertEqual(list(connected_cars()["company1"].keys()), ["car1", "car2"])
        remove_connected_device("company1", "car1", self.device_1_id)
        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(
            connected_cars(), {
                "company1": {
                    "car2": ConnectedCar("company1", "car2", 0, {
                        48: ConnectedModule(48, {serialized_device_id(self.device_x_id): self.device_x_id})
                    })
                }
            }
        )

    def test_cleaning_up_modules_without_any_device_ids(self):
        clear_connected_cars()
        add_car("company1", "car1", timestamp=0)
        add_device("company1", "car1", self.device_1_id, timestamp=0)
        add_device("company1", "car1", self.device_x_id, timestamp=0)
        remove_connected_device("company1", "car1", self.device_x_id)

        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(
            connected_cars(),
            {
                "company1": {
                    "car1": ConnectedCar(
                        "company1",
                        "car1",
                        0,
                        {
                            45: ConnectedModule(45, {
                                serialized_device_id(self.device_1_id): self.device_1_id
                            })
                        }
                    )
                }
            },
        )

    def test_cleaning_up_companies_without_any_cars(self):
        clear_connected_cars()
        add_car("company1", "car1", timestamp=0)
        add_car("company2", "car1", timestamp=0)
        add_car("company3", "carA", timestamp=0)
        add_car("company3", "carB", timestamp=0)
        add_device("company1", "car1", self.device_1_id, timestamp=0)
        add_device("company3", "carA", self.device_123_id, timestamp=0)
        add_device("company3", "carB", self.device_456_id, timestamp=0)
        remove_connected_device("company2", "car1", self.device_x_id)
        clean_up_disconnected_cars_and_modules()
        self.assertListEqual(list(connected_cars().keys()), ["company1", "company3"])

        remove_connected_device("company1", "car1", self.device_1_id)
        clean_up_disconnected_cars_and_modules()
        self.assertListEqual(list(connected_cars().keys()), ["company3"])

    def test_cleaning_up_empty_device_ids_dict_has_no_effect(self):
        clear_connected_cars()
        clean_up_disconnected_cars_and_modules()
        self.assertDictEqual(connected_cars(), {})


if __name__ == "__main__":
    unittest.main()

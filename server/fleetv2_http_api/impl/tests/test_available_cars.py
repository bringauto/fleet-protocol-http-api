import sys

sys.path.append("server")
from enums import MessageType, EncodingType  # type: ignore
import unittest

sys.path.append("server")


from enums import MessageType, EncodingType  # type: ignore
from database.connected_cars import clear_connected_cars, connected_cars # type: ignore
from database.database_controller import (   # type: ignore
    set_test_db_connection,
)
from fleetv2_http_api.impl.controllers import (  # type: ignore
    available_cars,
    send_statuses
)
from fleetv2_http_api.models import DeviceId, Payload, Message, Car # type: ignore

class Test_Listing_Available_Devices_And_Cars(unittest.TestCase):
    def setUp(self) -> None:
        set_test_db_connection("/:memory:")
        payload = Payload(
            message_type=MessageType.STATUS_TYPE,
            encoding=EncodingType.JSON,
            data={"message": "Device is running"},
        )
        self.device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Left light")
        self.status = Message(
            timestamp=123456789, device_id=self.device_id, payload=payload
        )
        clear_connected_cars()

    def test_car_is_available_if_at_least_one_status_is_in_the_database(self):
        send_statuses("test_company", "test_car", body=[self.status])
        self.assertEqual(len(connected_cars().keys()), 1)
        self.assertEqual(len(available_cars()[0]), 1)
        send_statuses("other_company", "car_a", body=[self.status])
        self.assertEqual(len(connected_cars().keys()), 2)
        self.assertEqual(len(available_cars()[0]), 2)
        self.assertListEqual(
            available_cars()[0],
            [
                Car(company_name="test_company", car_name="test_car"),
                Car(company_name="other_company", car_name="car_a"),
            ]
        )
        send_statuses("other_company", "car_b", body=[self.status])
        self.assertEqual(len(connected_cars().keys()), 2)
        self.assertEqual(len(available_cars()[0]), 3)
        self.assertListEqual(
            available_cars()[0],
            [
                Car(company_name="test_company", car_name="test_car"),
                Car(company_name="other_company", car_name="car_a"),
                Car(company_name="other_company", car_name="car_b"),
            ]
        )


if __name__ == "__main__":
    unittest.main()

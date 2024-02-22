import unittest
import sys

sys.path.append("server")

import server.app as _app
from server.fleetv2_http_api.models.message import Message, Payload, DeviceId
from server.enums import MessageType


class Test_Company_And_Car_Name_Not_Following_Pattern_From_OpenAPI_Spec_Yield_Code_400(unittest.TestCase):
    def setUp(self) -> None:
        self.app = _app.get_test_app(base_url="/v2/protocol/")
        self.device_id = DeviceId(module_id=7, type=8, role="test_device", name="Test Device")
        self.payload = Payload(
            message_type=MessageType.STATUS_TYPE,
            encoding="JSON",
            data={"phone_number": "1234567890"},
        )
        self.status = Message(device_id=self.device_id, payload=self.payload)
        self.invalid_car_names = ["test car", "test-car", "TestCar", "    ", "$$$"]
        self.invalid_company_names = ["test company", "test-company", "TestCompany", "    ", "$$$"]

    def test_status_endpoint(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_car_name in self.invalid_car_names:
                with self.subTest(invalid_car_name=invalid_car_name):
                    response = client.get(f"/status/valid_company_name/{invalid_car_name}", json=[self.status])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("pattern", response.json["detail"]) # type: ignore
            for invalid_company_name in self.invalid_company_names:
                with self.subTest(invalid_company_name=invalid_company_name):
                    response = client.get(f"/status/{invalid_company_name}/valid_car_name", json=[self.status])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("pattern", response.json["detail"]) # type: ignore

    def test_command_endpoint(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_car_name in self.invalid_car_names:
                with self.subTest(invalid_car_name=invalid_car_name):
                    response = client.get(f"/command/valid_company_name/{invalid_car_name}", json=[self.status])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("pattern", response.json["detail"]) # type: ignore
            for invalid_company_name in self.invalid_company_names:
                with self.subTest(invalid_company_name=invalid_company_name):
                    response = client.get(f"/command/{invalid_company_name}/valid_car_name", json=[self.status])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("pattern", response.json["detail"]) # type: ignore

    def test_available_device_endpoint(self) -> None:
        with self.app.app.test_client() as client:
            for invalid_car_name in self.invalid_car_names:
                with self.subTest(invalid_car_name=invalid_car_name):
                    response = client.get(f"/available-devices/valid_company_name/{invalid_car_name}", json=[self.status])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("pattern", response.json["detail"]) # type: ignore
            for invalid_company_name in self.invalid_company_names:
                with self.subTest(invalid_company_name=invalid_company_name):
                    response = client.get(f"/available-devices/{invalid_company_name}/valid_car_name", json=[self.status])
                    self.assertEqual(response.status_code, 400)
                    self.assertIn("pattern", response.json["detail"]) # type: ignore

    def tearDown(self) -> None:
        self.app.clear_all()


if __name__=="__main__":
    unittest.main(verbosity=2, buffer=True)
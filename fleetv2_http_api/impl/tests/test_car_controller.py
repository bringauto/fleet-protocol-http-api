import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.car_controller import *


class Test_Nothing(unittest.TestCase):

    def test_adding_and_retrieving_single_car(self):
        car = Car(company_name="test_company_123", car_name="test_car_456")
        add_car(car)
        self.assertListEqual(cars_available(), [car])


if __name__=="__main__":
    unittest.main()
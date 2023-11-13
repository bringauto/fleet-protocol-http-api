import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.database_controller import set_connection_source
from fleetv2_http_api.impl.car_controller import _add_car, cars_available, _clear_cars, Car


class Test_Listing_Available_Cars(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source("sqlite","pysqlite","/:memory:")

    def test_adding_and_retrieving_single_car(self):
        car = Car(company_name="test_company_123", car_name="test_car_456")
        _add_car(car)
        self.assertListEqual(cars_available(), [car])

    def test_checking_company__and_car_name_validity(self):
        # The car can be initialized with invalid car an company name.
        # The pattern mathching is done only when setting company/car name 
        # of an existing car!!!
        car = Car(company_name="valid_name", car_name="brand_new_car")
        car.company_name = "other_valid_name"
        self.assertEqual(car.company_name, "other_valid_name")
        with self.assertRaises(ValueError): car.company_name = "name with spaces"
        with self.assertRaises(ValueError): car.company_name = "Name" # lowercase is required
        with self.assertRaises(ValueError): car.company_name = ""
        with self.assertRaises(ValueError): car.company_name = "  "

        car.car_name = "relativelly_new_car"
        self.assertEqual(car.car_name, "relativelly_new_car")
        with self.assertRaises(ValueError): car.car_name = "name with spaces"
        with self.assertRaises(ValueError): car.car_name = "Name" # lowercase is required
        with self.assertRaises(ValueError): car.car_name = ""
        with self.assertRaises(ValueError): car.car_name = "  "



class Test_PostgreSQL_Database(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source(
            dialect="postgresql",
            dbapi="psycopg",
            dblocation="localhost:5432",
            username="postgres",
            password="1234"
        )
        _clear_cars()

    def test_adding_and_retrieving_single_car(self):
        car = Car(company_name="test_company_123", car_name="test_car_456")
        _add_car(car)
        self.assertListEqual(cars_available(), [car])

    def tearDown(self) -> None:
        _clear_cars()


if __name__=="__main__":
    unittest.main()
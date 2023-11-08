import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.car_controller import new_connection_source, set_connection_source
from fleetv2_http_api.impl.car_controller import add_car, cars_available, _clear_cars, Car
from sqlalchemy import text


class Test_Set_Up_Connection_Source(unittest.TestCase):

    def test_creating_connection_engine(self):
        src = new_connection_source("sqlite","pysqlite","/:memory:")
        with src.connect() as conn:
            conn.execute(text("CREATE TABLE some_table (id INTEGER, name STRING, PRIMARY KEY (id))"))
            conn.commit()


class Test_Listing_Available_Cars(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source(new_connection_source("sqlite","pysqlite","/:memory:"))

    def test_adding_and_retrieving_single_car(self):
        car = Car(company_name="test_company_123", car_name="test_car_456")
        add_car(car)
        self.assertListEqual(cars_available(), [car])


class Test_PostgreSQL_Database(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source(
            new_connection_source(
                dialect="postgresql",
                dbapi="psycopg",
                dblocation="localhost:5432",
                username="postgres",
                password="1234"
            )
        )
        _clear_cars()

    def test_adding_and_retrieving_single_car(self):
        car = Car(company_name="test_company_123", car_name="test_car_456")
        add_car(car)
        self.assertListEqual(cars_available(), [car])

    def tearDown(self) -> None:
        _clear_cars()


if __name__=="__main__":
    unittest.main()
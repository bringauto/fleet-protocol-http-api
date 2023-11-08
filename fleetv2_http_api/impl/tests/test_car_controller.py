import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.car_controller import new_connection_source, add_car, cars_available, Car
from fleetv2_http_api.impl.car_controller import set_connection_source
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



if __name__=="__main__":
    unittest.main()
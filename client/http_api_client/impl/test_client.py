import sys
sys.path.append(".")
sys.path.append("..")

from http_api_client.impl.client import Client
from http_api_client.models import Car
import unittest


class Test_Operator(unittest.TestCase):

	def setUp(self) -> None:
		self.client = Client("http://localhost:8080")
		self.client.connect_to_database(
			dialect="postgresql",
			dbapi="psycopg",
			location="localhost:5432",
			username="postgres",
			password="1234"
		)

	def test_clients_can_get_list_of_cars_after_connecting_to_database(self)->None:
		self.assertTrue(type(self.client.api.cars_available())==list)


	def test_adding_and_viewing_new_car(self)->None:
		try:
			self.client.api.add_car(Car(car_name="test_car", company_name="test_company"))
		except: 
			print("Car 'test_car' already exists in the database.")
		self.assertTrue(
			Car(car_name="test_car", company_name="test_company") in self.client.api.cars_available()
		)

	


if __name__=="__main__":
	unittest.main()

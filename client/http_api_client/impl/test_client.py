import sys
sys.path.append(".")

from http_api_client.impl.client import Client
import unittest


class Test_Operator(unittest.TestCase):

	def test_message_from_the_server(self)->None:
		op = Client("http://localhost:8080")
		op.connect_to_database(
			dialect="postgresql",
			dbapi="psycopg",
			location="localhost:5432",
			username="postgres",
			password="1234"
        )
		# # self.assertEqual(op.api.cars_available(), [])


if __name__=="__main__":
	unittest.main()

import  sys
sys.path.append("server")


import unittest
from unittest.mock import patch
from database.database_connection import set_db_connection
from database.security import get_client, add_client, clear_loaded_clients


class Test_Getting_Client(unittest.TestCase):

    def setUp(self) -> None:
        set_db_connection(
            dialect="sqlite",
            dbapi="pysqlite",
            dblocation="/:memory:",
            username="",
            password=""
        )
        clear_loaded_clients()

    @patch("database.security.__generate_key")
    def test_getting_client_from_database(self, mock_generate_key):
        self.assertTrue(get_client("1234567890", "visitor") is None)
        mock_generate_key.return_value = "1234567890"
        add_client("Alice", "visitor")
        self.assertTrue(get_client("1234567890", "visitor") is not None)
        
    @patch("database.security.__generate_key")
    def test_clients_are_distinguished_by_their_types(self, mock_generate_key):
        mock_generate_key.return_value = "1234567890"
        add_client("Alice", "visitor")
        # the key was not defined for the type 'operator'
        self.assertTrue(get_client("1234567890", "operator") is None)

        

if __name__=="__main__":
    unittest.main()

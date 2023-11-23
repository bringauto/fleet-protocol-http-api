import  sys
sys.path.append("server")


import unittest
from unittest.mock import patch
from database.database_connection import set_db_connection
from database.security import get_admin, add_admin, clear_loaded_admins


class Test_Getting_Client(unittest.TestCase):

    def setUp(self) -> None:
        set_db_connection(
            dialect="sqlite",
            dbapi="pysqlite",
            dblocation="/:memory:",
            username="",
            password=""
        )
        clear_loaded_admins()

    @patch("database.security.__generate_key")
    def test_getting_admin_from_database(self, mock_generate_key):
        self.assertTrue(get_admin("1234567890") is None)
        mock_generate_key.return_value = "1234567890"
        add_admin("Alice")
        self.assertTrue(get_admin("1234567890") is not None)
        

        

if __name__=="__main__":
    unittest.main()

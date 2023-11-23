import  sys
sys.path.append("server")


import unittest
from unittest.mock import patch, Mock
from database.database_connection import set_db_connection
from database.security import (
    get_admin,
    add_admin, 
    clear_loaded_admins, 
    Admin_DB, 
    get_loaded_admins,
    number_of_admins
)


class Test_Getting_Admin(unittest.TestCase):

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
    def test_getting_admin_from_database(self, mock_generate_key:Mock):
        self.assertTrue(get_admin("1234567890") is None)
        mock_generate_key.return_value = "1234567890"
        add_admin("Alice")
        self.assertTrue(get_admin("1234567890") is not None)
        
    @patch("database.security.__generate_key")
    def test_getting_admin_not_yet_loaded(self, mock_generate_key:Mock)->None:
        mock_generate_key.return_value = "abcdef"

        add_admin("Alice")
        expected_admin = Admin_DB(id=1, name="Alice", key="abcdef")

        self.assertListEqual(get_loaded_admins(), [])
        # if the admin is accessed for the first time, it is loaded from the database
        admin = get_admin("abcdef")
        self.assertEqual(admin, expected_admin)
        self.assertListEqual(get_loaded_admins(), [expected_admin])
        # if the admin is accessed for the first time, it is not queried again, neither it is 
        # again added to the list of loaded admins
        get_admin("abcdef")
        self.assertListEqual(get_loaded_admins(), [expected_admin])

    def test_getting_nonexistent_admin_returns_none(self)->None:
        self.assertTrue(get_admin("nonexistent_key") is None)
     
    def test_number_of_admins_in_database(self)->None:
        add_admin("Alice")
        self.assertEqual(number_of_admins(), 1)
        add_admin("Bob")
        self.assertEqual(number_of_admins(), 2)


if __name__=="__main__":
    unittest.main()

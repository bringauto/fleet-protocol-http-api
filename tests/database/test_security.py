import sys

sys.path.append(".")

import unittest
from unittest.mock import patch, Mock
from server.database.connection import set_test_db_connection
from server.database.security import (
    get_admin,
    add_admin_key,
    clear_loaded_admins,
    AdminDB,
    get_loaded_admins,
    number_of_admin_keys,
)


class Test_Getting_Admin(unittest.TestCase):
    def setUp(self) -> None:
        set_test_db_connection(dblocation="/:memory:")
        clear_loaded_admins()

    @patch("server.database.security._generate_key")
    def test_getting_admin_from_database(self, mock_generate_key: Mock):
        self.assertTrue(get_admin("1234567890") is None)
        mock_generate_key.return_value = "1234567890"
        add_admin_key("Alice")
        self.assertTrue(get_admin("1234567890") is not None)

    @patch("server.database.security._generate_key")
    def test_getting_admin_not_yet_loaded(self, mock_generate_key: Mock) -> None:
        mock_generate_key.return_value = "abcdef"

        add_admin_key("Alice")
        expected_admin = AdminDB(id=1, name="Alice", key="abcdef")

        self.assertListEqual(get_loaded_admins(), [])
        # if the admin is accessed for the first time, it is loaded from the database
        admin = get_admin("abcdef")
        self.assertEqual(admin, expected_admin)
        self.assertListEqual(get_loaded_admins(), [expected_admin])
        # if the admin is accessed for the first time, it is not queried again, neither it is
        # again added to the list of loaded admins
        get_admin("abcdef")
        self.assertListEqual(get_loaded_admins(), [expected_admin])

    def test_getting_nonexistent_admin_returns_none(self) -> None:
        self.assertTrue(get_admin("nonexistent_key") is None)

    def test_number_of_admins_in_database(self) -> None:
        add_admin_key("Alice")
        self.assertEqual(number_of_admin_keys(), 1)
        add_admin_key("Bob")
        self.assertEqual(number_of_admin_keys(), 2)


if __name__ == "__main__":
    unittest.main()

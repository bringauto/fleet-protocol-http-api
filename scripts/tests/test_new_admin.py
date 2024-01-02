import sys
import os

import subprocess
import unittest

root_path = os.path.dirname(os.path.dirname(sys.path[0]))
sys.path[0] = root_path
sys.path.append("server")

from server.database.connection import set_test_db_connection, get_connection_source, unset_connection_source
from server.database.security import number_of_admin_keys


DB_FILE_LOCATION = "/scripts/tests/example.db"


class Test_Adding_Admin(unittest.TestCase):

    def setUp(self) -> None: # pragma: no cover
        self.abs_db_path = os.path.abspath("."+DB_FILE_LOCATION)
        set_test_db_connection(DB_FILE_LOCATION)
        self.connection = get_connection_source()

    def test_adding_admin(self) -> None:
        subprocess.call('cd ..', shell=True)
        subprocess.run(
            [
                'python',
                'scripts/new_admin.py',
                "Alice",
                "config.json",
                "--location",
                DB_FILE_LOCATION,
                "--test",
                "True"
            ],
            capture_output=True
        )
        assert(self.connection is not None)
        self.assertEqual(number_of_admin_keys(self.connection), 1)

    def test_repeatedly_adding_admin_with_the_name_has_no_effect(self):
        args = ['python', 'scripts/new_admin.py', 'Alice', 'config.json', "--location", DB_FILE_LOCATION, "--test", "True"]
        self.assertEqual(number_of_admin_keys(self.connection), 0)
        subprocess.run(args, capture_output=True)
        self.assertEqual(number_of_admin_keys(self.connection), 1)
        subprocess.run(args, capture_output=True)
        self.assertEqual(number_of_admin_keys(self.connection), 1)

    def test_printing_new_admin_key_to_console(self):
        args = ['python', 'scripts/new_admin.py', 'Bob', 'config.json', "--location", DB_FILE_LOCATION, "--test", "True"]
        output = subprocess.run(args, capture_output=True)
        self.assertTrue("Bob" in output.stdout.decode())

    def tearDown(self) -> None:
        if os.path.exists(self.abs_db_path):
            os.remove(self.abs_db_path)


if __name__=="__main__":
    unittest.main()
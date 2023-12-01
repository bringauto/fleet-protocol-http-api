import sys, os


root_path = os.path.dirname(os.path.dirname(sys.path[0]))
sys.path[0] = root_path
sys.path.append("server")


import subprocess
import unittest
from server.database.connection import get_db_connection
from server.database.security import number_of_admins
import os


DB_FILE_LOCATION = "/example.db"


class Test_Adding_Admin(unittest.TestCase):

    def setUp(self) -> None: # pragma: no cover
        if os.path.exists("./scripts/tests/example.db"): 
            os.remove("./scripts/tests/example.db")
        self.connection = get_db_connection("sqlite","pysqlite",DB_FILE_LOCATION)

    def test_adding_admin(self):
        subprocess.run(['cd', '..'])
        subprocess.run(
            [
                'python3', 
                'new_admin.py',
                'Alice',
                "sqlite",
                "pysqlite",
                DB_FILE_LOCATION,
            ],
            capture_output=True
        )
        assert(self.connection is not None)
        self.assertEqual(number_of_admins(self.connection), 1)

    def test_repeatedly_adding_admin_with_the_name_has_no_effect(self):
        args = ['python3', 'new_admin.py', 'Alice', "sqlite", "pysqlite", DB_FILE_LOCATION]
        assert(self.connection is not None)
        subprocess.run(args, capture_output=True)
        self.assertEqual(number_of_admins(self.connection), 1)
        subprocess.run(args, capture_output=True)
        self.assertEqual(number_of_admins(self.connection), 1)

    def test_printing_new_admin_key_to_console(self):
        args = ['python3', 'new_admin.py', 'Bob', "sqlite", "pysqlite", DB_FILE_LOCATION]
        result = subprocess.run(args, capture_output=True)
        self.assertTrue("New key" in result.stdout.decode())



if __name__=="__main__": unittest.main()
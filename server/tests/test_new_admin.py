import sys
sys.path.append("server")


import subprocess
import unittest
from database.database_controller import set_db_connection
from database.security import number_of_admins
import os


DB_FILE_LOCATION = "/tests/example.db"


class Test_Adding_Admin(unittest.TestCase):

    def setUp(self) -> None: # pragma: no cover
        if os.path.exists("tests/example.db"): 
            os.remove("tests/example.db")
        set_db_connection("sqlite","pysqlite",DB_FILE_LOCATION)

    def test_adding_admin(self):
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
        self.assertEqual(number_of_admins(), 1)

    def test_repeatedly_adding_admin_with_the_name_has_no_effect(self):
        args = ['python3', 'new_admin.py', 'Alice', "sqlite", "pysqlite", DB_FILE_LOCATION]
        subprocess.run(args, capture_output=True)
        self.assertEqual(number_of_admins(), 1)
        subprocess.run(args, capture_output=True)
        self.assertEqual(number_of_admins(), 1)

    def test_printing_new_admin_key_to_console(self):
        args = ['python3', 'new_admin.py', 'Bob', "sqlite", "pysqlite", DB_FILE_LOCATION]
        result = subprocess.run(args, capture_output=True)
        self.assertTrue("New key" in result.stdout.decode("utf-8"))



if __name__=="__main__": unittest.main()
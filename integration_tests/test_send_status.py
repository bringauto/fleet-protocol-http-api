import unittest
import sys

sys.path.append('server')

from server.app import get_test_app
from server.database.connection import set_test_db_connection


class Test_Sending_First_Status(unittest.TestCase):

    def setUp(self) -> None:
        set_test_db_connection()
        self.app = get_test_app()


    def test_sending_status(self):
        with self.app.app.test_client() as c:
            pass


if __name__ == '__main__': # pragma: no cover
    unittest.main()
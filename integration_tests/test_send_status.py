import unittest

from server.app import get_app_test


class Test_Sending_First_Status(unittest.TestCase):

    def setUp(self) -> None:
        self.app = get_app_test()

    def test_sending_status(self):
        with self.app.app.test_client() as c:
            pass


if __name__ == '__main__': # pragma: no cover
    unittest.main()
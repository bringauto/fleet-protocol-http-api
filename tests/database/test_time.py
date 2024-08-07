import sys

sys.path.append(".")
import unittest
from unittest.mock import patch, Mock

from server.database.time import timestamp


class Test_Creating_And_Reading_MessageBase_Objects(unittest.TestCase):
    @patch("server.database.time._time_in_ms")
    def test_creating_time(self, mock_time_in_ms: Mock) -> None:
        mock_time_in_ms.return_value = 10000
        self.assertEqual(timestamp(), 10000)


if __name__ == "__main__":
    unittest.main()

import unittest
import sys
import os

sys.path.append(".")

from server.config import APIConfig, load_config_file


_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


class Test_Config(unittest.TestCase):

    def setUp(self):
        self.config_dict = load_config_file(os.path.join(_CURRENT_DIR, "./test_config.json"))

    def test_config(self):
        APIConfig(**self.config_dict)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

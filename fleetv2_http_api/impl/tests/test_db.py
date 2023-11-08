import sys
sys.path.append(".")


import unittest
from fleetv2_http_api.impl.db import set_connection_source, connection_source, unset_connection_source
from fleetv2_http_api.impl.db import Connection_Source_Not_Set
from sqlalchemy import text


class Test_Set_Up_Connection_Source(unittest.TestCase):

    def setUp(self) -> None:
        set_connection_source("sqlite","pysqlite","/:memory:")

    def test_creating_connection_source(self):
        with connection_source().connect() as conn:
            conn.execute(text("CREATE TABLE some_table (id INTEGER, name STRING, PRIMARY KEY (id))"))
            conn.commit()

    def test_accessing_connection_source(self):
        self.assertEqual(connection_source().dialect.name, "sqlite")
        unset_connection_source()
        with self.assertRaises(Connection_Source_Not_Set):
            connection_source().dialect.name


if __name__=="__main__":
    unittest.main()
import sys, os
sys.path[0] = os.path.abspath(os.path.join(sys.path[0], os.pardir))
sys.path.append("server")

from sqlalchemy.engine import Engine
from server.database.security import add_admin_key
from server.database.connection import get_db_connection, get_test_db_connection
from server.database.script_args import (
    request_and_get_script_arguments,
    PositionalArgInfo,
)

def _add_key_if_admin_name_not_already_in_db(connection_source: Engine, admin_name: str) -> None:
    """Try to add a new admin key to the database. If successfull, print the new API key, otherwise print
    message about already existing admin."""
    msg = add_admin_key(name=admin_name, connection_source=connection_source)
    print(msg)

if __name__=="__main__":
    vals = request_and_get_script_arguments(
        "Add a new admin to the database and if successful, print his or hers API key.",
        PositionalArgInfo("<admin-name>", str, "The name of the new admin.")
    )
    arguments = vals.argvals
    config = vals.config
    if arguments["test"]:
        source = get_test_db_connection(
            dblocation=arguments["location"],
            db_name=arguments["database_name"]
        )
    else:
        source = get_db_connection(
            dblocation=(arguments["location"]+":"+str(arguments["port"])),
            username=arguments["username"],
            password=arguments["password"],
            db_name=arguments["database_name"]
        )
    if source is not None:
        _add_key_if_admin_name_not_already_in_db(source, arguments["<admin-name>"])
    else:
        print("Could not connect to the database.")

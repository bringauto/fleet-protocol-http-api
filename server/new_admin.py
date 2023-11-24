from database.security import add_admin
from database.connection import set_db_connection, unset_connection_source
import sys
import dataclasses


@dataclasses.dataclass
class Args:
    admin_name:str
    db_dialect:str
    db_api:str  
    db_location:str
    db_username:str = ""
    db_password:str = ""


script_args = sys.argv[1:]


arguments = Args(
    admin_name = script_args[0],
    db_dialect = script_args[1],
    db_api = script_args[2],
    db_location = script_args[3],
)
if len(script_args)>4: arguments.db_username = script_args[4]
if len(script_args)>5: arguments.db_password = script_args[5]


set_db_connection(
    dialect = arguments.db_dialect,
    dbapi = arguments.db_api,
    dblocation = arguments.db_location,
    username = arguments.db_username,
    password = arguments.db_password
)

new_key = add_admin(name=arguments.admin_name)
if new_key != "":
    print(f"New key for admin '{arguments.admin_name}': {new_key}")
else:
    print(f"Admin '{arguments.admin_name}' already exists.")

unset_connection_source()


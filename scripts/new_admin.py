import sys, os

sys.path[0] = os.path.abspath(os.path.join(sys.path[0], os.pardir))
sys.path.append("server")


import argparse
from argparse import ArgumentParser
from typing import Dict, Any, Tuple
from sqlalchemy.engine import Engine


from server.database.security import add_admin
from server.database.connection import get_db_connection


def parse_arguments()->Tuple[ArgumentParser, Dict[str,Any]]:
    parser = argparse.ArgumentParser(description="Add a new admin to the database.")
    parser.add_argument("admin-name", type=str, help="The name of the new admin.")
    parser.add_argument("dialect", type=str, help="The database dialect.")
    parser.add_argument("db-api", type=str, help="The database API.")
    parser.add_argument("db-location", type=str, help="The database location.")
    parser.add_argument(
        "-usr", "--username", type=str, help="The username for the database.", default="", required=False
    )
    parser.add_argument(
        "-pwd", "--password", type=str, help="The password for the database.", default="", required=False
    )
    return parser, parser.parse_args().__dict__


def get_connection_to_database(parser:argparse.ArgumentParser, arguments:Dict[str,Any])->Engine:
    try:
        source = get_db_connection(
            dialect = arguments["dialect"],
            dbapi = arguments["db-api"],
            dblocation = arguments["db-location"],
            username = arguments["username"],
            password = arguments["password"]
        )
        if source == None:
            parser.error("No connection source obtained. Cannot connect to the database. Invalid database connection parameters.")
        return source
    
    except Exception as e:
        parser.error("Error when connecting to the database. Cannot connect to the database. Invalid database connection parameters.")
    

def try_to_add_key(connection_source:Engine, arguments:Dict[str,Any])->None:
    new_key = add_admin(name=arguments["admin-name"], connection_source=connection_source)
    if new_key != "": 
        print(f"\nNew key for admin '{arguments['admin-name']}':\n\n{new_key}\n")
    else: 
        print(f"Admin '{arguments['admin-name']}' already exists.")


if __name__=="__main__":
    parser, arguments = parse_arguments()
    source = get_connection_to_database(parser, arguments)
    try_to_add_key(source, arguments)

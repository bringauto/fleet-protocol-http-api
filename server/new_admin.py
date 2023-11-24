import argparse
from argparse import ArgumentParser
from typing import Dict, Any, Tuple


from database.security import add_admin
from database.connection import (
    set_db_connection, 
    unset_connection_source, 
    get_connection_source
)


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


def connect_to_database(parser:argparse.ArgumentParser, arguments:Dict[str,Any])->None:
    try:
        set_db_connection(
            dialect = arguments["dialect"],
            dbapi = arguments["db-api"],
            dblocation = arguments["db-location"],
            username = arguments["username"],
            password = arguments["password"]
        )
    except Exception as e:
        parser.error("Cannot connect to the database. Invalid database connection parameters.")
    if get_connection_source() == None:
        parser.error("Cannot connect to the database. Invalid database connection parameters.")


def try_to_add_key(arguments:Dict[str,Any])->None:
    new_key = add_admin(name=arguments["admin-name"])
    if new_key != "": 
        print(f"\nNew key for admin '{arguments['admin-name']}':\n\n{new_key}\n")
    else: 
        print(f"Admin '{arguments['admin-name']}' already exists.")


def disconnect_from_database()->None:
    unset_connection_source()


if __name__=="__main__":
    parser, arguments = parse_arguments()
    connect_to_database(parser, arguments)
    try_to_add_key(arguments)
    disconnect_from_database()

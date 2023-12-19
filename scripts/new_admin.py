import sys, os

sys.path[0] = os.path.abspath(os.path.join(sys.path[0], os.pardir))
sys.path.append("server")


import argparse
from argparse import ArgumentParser
from typing import Dict, Any, Tuple
from sqlalchemy.engine import Engine
import json


from server.database.security import add_admin_key
from server.database.connection import get_db_connection


EMPTY_VALUE = ""


def parse_arguments(config:Dict[str,str])->Tuple[ArgumentParser, Dict[str,str]]:
    parser = argparse.ArgumentParser(
        description="Add a new admin to the database and if successfull, print his or hers API key."
    )
    parser.add_argument("<admin-name>", type=str, help="The name of the new admin.")
    parser.add_argument(
        "-usr", "--username", type=str, help="The username for the database server.", default=EMPTY_VALUE, required=False
    )
    parser.add_argument(
        "-pwd", "--password", type=str, help="The password for the database server.", default=EMPTY_VALUE, required=False
    )
    parser.add_argument(
        "-l", "--location", type=str, help="The location/address of the database", default=EMPTY_VALUE, required=False
    )
    parser.add_argument(
        "-p", "--port", type=str, help="The database port number.", default=EMPTY_VALUE, required=False
    )
    args = parser.parse_args().__dict__
    for key in args:
        if args[key] == EMPTY_VALUE: args[key] = config[key]
    return parser, args


def get_connection_to_database(
    dblocation:str,
    username:str,
    password:str
    )->Engine:
    
    source = get_db_connection(
        dblocation,
        username,
        password
    )
    return source


def try_to_add_key(connection_source:Engine, admin_name:str)->None:
    """Try to add a new admin key to the database. If successfull, print the new API key, otherwise print 
    message about already existing admin."""
    msg = add_admin_key(name=admin_name, connection_source=connection_source)
    print(msg)


import os
if __name__=="__main__":
    root_dir = os.path.dirname(os.path.dirname(__file__))
    config:Dict[str,Any] = json.load(open(os.path.join(root_dir, "config.json")))["database"]["server"]
    arguments = parse_arguments(config)
    source = get_connection_to_database(
        dblocation=(arguments["location"]+":"+str(arguments["port"])),
        username=arguments["username"],
        password=arguments["password"]
    )
    try_to_add_key(source, arguments["<admin-name>"])

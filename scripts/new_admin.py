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


import dataclasses
@dataclasses.dataclass(frozen=True)
class Arg_Values:
    config:Dict[str,Any]
    sysargs:Dict[str,str]

    def get(self, key:str)->Any:
        """Return the value of the argument with the given key. If the value is not specified by user running the script,
        take value from the config file."""
        if key in self.sysargs and not (self.sysargs[key].strip()=="" or self.sysargs[key] is None): 
            return self.sysargs[key]
        elif key in self.config: 
            return self.config[key]
        else: 
            raise KeyError(f"Argument '{key}' not found in sysargs nor the config file.")


def parse_arguments()->Tuple[ArgumentParser, Dict[str,Any]]:
    parser = argparse.ArgumentParser(
        description="Add a new admin to the database and if successfull, print his or hers API key."
    )
    parser.add_argument("<admin-name>", type=str, help="The name of the new admin.")
    parser.add_argument(
        "-usr", "--username", type=str, help="The username for the database server.", default="", required=False
    )
    parser.add_argument(
        "-pwd", "--password", type=str, help="The password for the database server.", default="", required=False
    )
    parser.add_argument(
        "-l", "--location", type=str, help="The location/address of the database", default="", required=False
    )
    parser.add_argument(
        "-p", "--port", type=str, help="The database port number.", default="", required=False
    )
    args = parser.parse_args().__dict__
    return parser, args


def get_connection_to_database(
    parser:argparse.ArgumentParser,
    dblocation:str,
    username:str,
    password:str
    )->Engine:
    
    try:
        source = get_db_connection(
            dblocation,
            username,
            password
        )
        if source == None:
            parser.error("No connection source obtained. Cannot connect to the database. Invalid database connection parameters.")
        return source
    
    except Exception as e:
        parser.error("Error when connecting to the database. Cannot connect to the database. Invalid database connection parameters.")
    

def try_to_add_key(connection_source:Engine, arguments:Dict[str,Any])->None:
    new_key = add_admin_key(name=arguments["<admin-name>"], connection_source=connection_source)
    if new_key != "": 
        print(f"\nNew key for admin '{arguments['<admin-name>']}':\n\n{new_key}\n")
    else: 
        print(f"Admin '{arguments['<admin-name>']}' already exists.")


import os
if __name__=="__main__":
    root_dir = os.path.dirname(os.path.dirname(__file__))
    config:Dict[str,Any] = json.load(open(os.path.join(root_dir, "config.json")))["database"]["server"]
    parser, arguments = parse_arguments()
    arg_vals = Arg_Values(config, arguments)

    source = get_connection_to_database(
        parser, 
        dblocation=(arg_vals.get("location")+":"+str(arg_vals.get("port"))),
        username=arg_vals.get("username"),
        password=arg_vals.get("password")
    )

    try_to_add_key(source, arguments)

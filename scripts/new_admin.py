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


def parse_arguments()->Tuple[ArgumentParser, Dict[str,Any]]:
    parser = argparse.ArgumentParser(description="Add a new admin to the database and if successfull, print his or hers API key.")
    parser.add_argument("<admin-name>", type=str, help="The name of the new admin.")
    return parser, parser.parse_args().__dict__


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
    source = get_connection_to_database(
        parser, 
        dblocation=(config["location"]+":"+str(config["port"])),
        username=config["username"],
        password=config["password"]
    )
    try_to_add_key(source, arguments)

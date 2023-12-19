import sys, os

sys.path[0] = os.path.abspath(os.path.join(sys.path[0], os.pardir))
sys.path.append("server")


import argparse
from typing import Dict, Any
from sqlalchemy.engine import Engine
import json


from server.database.security import add_admin_key
from server.database.connection import get_db_connection


EMPTY_VALUE = ""


def __get_arguments()->Dict[str,str]:
    parser = __new_arg_parser()
    __add_args_to_parser(parser)
    arguments = __parse_arguments(parser)
    return arguments


def __new_arg_parser()->argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Add a new admin to the database and if successful, print his or hers API key."
    )
    return parser


def __add_args_to_parser(parser:argparse.ArgumentParser)->None:
    parser.add_argument(
        "<admin-name>", type=str, help="The name of the new admin."
    )
    parser.add_argument(
        "-c", "--config-file-path", type=str, help="The path to the config file.", default="config.json", required=True
    )
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


def __load_condig_file(path:str)->Dict[str,Any]:
    try:
        config = json.load(open(path))
    except:
        raise Config_File_Not_Found(f"Could not load config file from path '{path}'.")
    return config

def __parse_arguments(parser:argparse.ArgumentParser)->Dict[str,str]:
    args = parser.parse_args().__dict__
    config = __load_condig_file(args.pop("config_file_path"))
    db_config = config["database"]["server"]
    for key in args:
        if args[key] == EMPTY_VALUE: args[key] = db_config[key]
    return args

def __try_to_add_key(connection_source:Engine, admin_name:str)->None:
    """Try to add a new admin key to the database. If successfull, print the new API key, otherwise print 
    message about already existing admin."""
    msg = add_admin_key(name=admin_name, connection_source=connection_source)
    print(msg)


class Config_File_Not_Found(Exception): pass


if __name__=="__main__":
    arguments = __get_arguments()
    source = get_db_connection(
        dblocation=(arguments["location"]+":"+str(arguments["port"])),
        username=arguments["username"],
        password=arguments["password"]
    )
    __try_to_add_key(source, arguments["<admin-name>"])

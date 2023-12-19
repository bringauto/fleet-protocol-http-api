import dataclasses
from typing import Type, Dict, Any
import argparse
import json


@dataclasses.dataclass
class Positional_Arg_Info:
    name:str
    type:Type
    help:str



EMPTY_VALUE = ""


def add_config_arg_to_parser(parser:argparse.ArgumentParser)->None:
    parser.add_argument(
        "-c", "--config-file-path", type=str, help="The path to the config file.", default="config.json", required=True
    )


def add_db_args_to_parser(parser:argparse.ArgumentParser)->None:
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


def add_positional_args_to_parser(parser:argparse.ArgumentParser, *args:Positional_Arg_Info)->None:
    for arg in args:
        parser.add_argument(arg.name, type=arg.type, help=arg.help)


def new_arg_parser(script_description:str, *positional_args:Positional_Arg_Info)->argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=script_description
    )
    return parser


def load_config_file(path:str)->Dict[str,Any]:
    try:
        config = json.load(open(path))
    except:
        raise Config_File_Not_Found(f"Could not load config file from path '{path}'.")
    return config


def request_and_get_script_arguments(
    script_description:str, 
    *positional_args:Positional_Arg_Info, 
    use_config:bool=True, 
    include_db_args:bool=True
    )->Dict[str,str]:

    parser = new_arg_parser(script_description)
    add_positional_args_to_parser(parser, *positional_args)
    if include_db_args:
        add_db_args_to_parser(parser)
    if use_config:
        add_config_arg_to_parser(parser)
    arguments = parse_arguments(parser, use_config)
    return arguments


def parse_arguments(parser:argparse.ArgumentParser, use_config:bool)->Dict[str,str]:
    args = parser.parse_args().__dict__
    config = load_config_file(args.pop("config_file_path"))
    db_config = config["database"]["server"]

    if use_config:
        for key in args:
            if args[key] == EMPTY_VALUE: args[key] = db_config[key]

    return args




class Config_File_Not_Found(Exception): pass
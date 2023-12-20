import dataclasses
from typing import Type, Dict, Any
import argparse
import json


@dataclasses.dataclass
class Positional_Arg_Info:
    name: str
    type:Type
    help: str



EMPTY_VALUE = ""


@dataclasses.dataclass(frozen=True)
class Script_Args:
    argvals: Dict[str,str]
    config: Dict[str,Any] = dataclasses.field(default_factory=dict)


def request_and_get_script_arguments(
    script_description: str,
    *positional_args:Positional_Arg_Info,
    use_config:bool=True,
    include_db_args:bool=True
    ) -> Dict[str,str]:

    parser = __new_arg_parser(script_description)

    __add_positional_args_to_parser(parser, *positional_args)
    if use_config:
        __add_config_arg_to_parser(parser)
    if include_db_args:
        __add_db_args_to_parser(parser)
    return __parse_arguments(parser, use_config)


def __add_config_arg_to_parser(parser:argparse.ArgumentParser) -> None:
    parser.add_argument("<config-file-path>", type=str, help="The path to the config file.", default="config.json")


def __add_db_args_to_parser(parser:argparse.ArgumentParser) -> None:
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


def __add_positional_args_to_parser(parser:argparse.ArgumentParser, *args:Positional_Arg_Info) -> None:
    for arg in args:
        parser.add_argument(arg.name, type=arg.type, help=arg.help)


def __new_arg_parser(script_description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=script_description)


def __load_config_file(path: str) -> Dict[str,Any]:
    try:
        config = json.load(open(path))
    except:
        raise Config_File_Not_Found(f"Could not load config file from path '{path}'.")
    return config


def __parse_arguments(parser:argparse.ArgumentParser, use_config:bool) -> Dict[str,str]:
    args = parser.parse_args().__dict__
    config = __load_config_file(args.pop("<config-file-path>"))
    db_config = config["database"]["server"]

    if use_config:
        for key in args:
            if args[key] == EMPTY_VALUE: args[key] = db_config[key]

    return Script_Args(args, config)


class Config_File_Not_Found(Exception): pass
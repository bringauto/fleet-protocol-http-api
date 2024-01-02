import dataclasses
from typing import Type, Dict, Any
import argparse
import json

EMPTY_VALUE = None


@dataclasses.dataclass
class PositionalArgInfo:
    name: str
    type:Type
    help: str


@dataclasses.dataclass(frozen=True)
class ScriptArgs:
    argvals: Dict[str,str]
    config: Dict[str,Any] = dataclasses.field(default_factory=dict)


def request_and_get_script_arguments(
    script_description: str,
    *positional_args:PositionalArgInfo,
    use_config:bool=True,
    include_db_args:bool=True
    ) -> Dict[str,str]:

    parser = _new_arg_parser(script_description)
    _add_positional_args_to_parser(parser, *positional_args)
    if use_config:
        _add_config_arg_to_parser(parser)
    if include_db_args:
        _add_db_args_to_parser(parser)
    return _parse_arguments(parser, use_config)

def _add_config_arg_to_parser(parser:argparse.ArgumentParser) -> None:
    parser.add_argument("<config-file-path>", type=str, help="The path to the config file.", default="config.json")

def _add_db_args_to_parser(parser:argparse.ArgumentParser) -> None:
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
    parser.add_argument(
        "-db", "--database-name", type=str, help="The name of the database.", default=EMPTY_VALUE, required=False
    )
    parser.add_argument(
        "-t", "--test", type=bool, help="Connect to a sqlite database. Username and password are ignored.", default=False, required=False
    )

def _add_positional_args_to_parser(parser:argparse.ArgumentParser, *args:PositionalArgInfo) -> None:
    for arg in args:
        parser.add_argument(arg.name, type=arg.type, help=arg.help)

def _new_arg_parser(script_description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=script_description)

def _load_config_file(path: str) -> Dict[str,Any]:
    try:
        config = json.load(open(path))
    except:
        raise ConfigFileNotFound(f"Could not load config file from path '{path}'.")
    return config

def _parse_arguments(parser:argparse.ArgumentParser, use_config:bool) -> Dict[str,str]:
    args = parser.parse_args().__dict__
    config = _load_config_file(args.pop("<config-file-path>"))
    db_config = config["database"]["server"]

    if use_config:
        for key in args:
            if args[key] == EMPTY_VALUE: args[key] = db_config[key]

    return ScriptArgs(args, config)


class ConfigFileNotFound(Exception): pass
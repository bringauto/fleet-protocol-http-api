import dataclasses
from typing import Type, Any
import argparse
import json

from server.config import APIConfig, DBServer


EMPTY_VALUE = None


@dataclasses.dataclass
class PositionalArgInfo:
    name: str
    type: Type
    help: str


@dataclasses.dataclass(frozen=True)
class ScriptArgs:
    argvals: dict[str, str]
    config: APIConfig


def request_and_get_script_arguments(
    script_description: str,
    *positional_args: PositionalArgInfo,
    include_db_args: bool = True,
) -> ScriptArgs:

    parser = _new_arg_parser(script_description)
    _add_positional_args_to_parser(parser, *positional_args)
    _add_config_arg_to_parser(parser)
    if include_db_args:
        _add_db_args_to_parser(parser)
    return _parse_arguments(parser)


def _add_config_arg_to_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "<config-file-path>", type=str, help="The path to the config file.", default="config.json"
    )


def _add_db_args_to_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-usr",
        "--username",
        type=str,
        help="The username for the database server.",
        default=EMPTY_VALUE,
        required=False,
    )
    parser.add_argument(
        "-pwd",
        "--password",
        type=str,
        help="The password for the database server.",
        default=EMPTY_VALUE,
        required=False,
    )
    parser.add_argument(
        "-l",
        "--location",
        type=str,
        help="The location/address of the database",
        default=EMPTY_VALUE,
        required=False,
    )
    parser.add_argument(
        "-p",
        "--port",
        type=str,
        help="The database port number.",
        default=EMPTY_VALUE,
        required=False,
    )
    parser.add_argument(
        "-db",
        "--database-name",
        type=str,
        help="The name of the database.",
        default=EMPTY_VALUE,
        required=False,
    )
    parser.add_argument(
        "-t",
        "--test",
        type=bool,
        help="Connect to a sqlite database. Username and password are ignored.",
        default=False,
        required=False,
    )


def _add_positional_args_to_parser(
    parser: argparse.ArgumentParser, *args: PositionalArgInfo
) -> None:
    for arg in args:
        parser.add_argument(arg.name, type=arg.type, help=arg.help)


def _new_arg_parser(script_description: str) -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description=script_description)


def _load_config_file(path: str) -> dict[str, Any]:
    try:
        config = json.load(open(path))
    except FileNotFoundError:
        raise ConfigFileNotFound(f"Could not load config file from path '{path}'.")
    return config


def _parse_arguments(parser: argparse.ArgumentParser) -> ScriptArgs:
    args = parser.parse_args().__dict__
    config_dict = _load_config_file(args.pop("<config-file-path>"))
    config = APIConfig(**config_dict)

    if isinstance(config.database.server, DBServer):
        db_config = config_dict["database"]["server"]
        for key in args:
            if args[key] == EMPTY_VALUE:
                args[key] = db_config[key]

    return ScriptArgs(args, config)


class ConfigFileNotFound(Exception):
    pass

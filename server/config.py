from __future__ import annotations
from typing import Any
import pydantic
import json


class APIConfig(pydantic.BaseModel):
    logging: Logging
    http_server: HTTPServer
    database: Database
    request_for_messages: MessageRequest
    security: Security


class Logging(pydantic.BaseModel):
    log_path: str
    verbose: bool


class HTTPServer(pydantic.BaseModel):
    base_uri: pydantic.AnyUrl
    port: pydantic.PositiveInt


class Security(pydantic.BaseModel):
    keycloak_url: pydantic.AnyUrl
    client_id: str
    client_secret_key: str
    scope: str
    realm: str


class MessageRequest(pydantic.BaseModel):
    timeout_in_seconds: pydantic.PositiveFloat


class Database(pydantic.BaseModel):
    server: DBServer
    cleanup: DatabaseCleanup


class DBServer(pydantic.BaseModel):
    username: str
    password: str
    location: str
    port: int
    database_name: str


class DatabaseCleanup(pydantic.BaseModel):
    timing_in_seconds: CleanupTiming


class CleanupTiming(pydantic.BaseModel):
    retention_period: pydantic.PositiveInt
    cleanup_period: pydantic.PositiveInt


def load_config_file(path: str) -> dict[str, Any]:
    try:
        with open(path) as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        raise ConfigFileNotFound(f"Could not load config file from path '{path}'.")
    except Exception as e:
        raise ValueError(f"Error when loading the config file: {e}")


class ConfigFileNotFound(Exception):
    pass

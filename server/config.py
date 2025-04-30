from __future__ import annotations
from typing import Any, Literal
import pydantic
import json


LoggingLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
from server.fleetv2_http_api.impl.security import SecurityConfig as SecurityConfig


class APIConfig(pydantic.BaseModel):
    logging: Logging
    http_server: HTTPServer
    database: Database
    request_for_messages: MessageRequest
    security: SecurityConfig


class Logging(pydantic.BaseModel):
    console: HandlerConfig
    file: HandlerConfig

    class HandlerConfig(pydantic.BaseModel):
        level: LoggingLevel
        use: bool
        path: str = ""

        @pydantic.field_validator("level", mode="before")
        @classmethod
        def validate_command(cls, level: str) -> str:
            return level.upper()


class HTTPServer(pydantic.BaseModel):
    base_uri: pydantic.AnyUrl
    port: pydantic.PositiveInt


class MessageRequest(pydantic.BaseModel):
    timeout_in_seconds: pydantic.PositiveFloat


class Database(pydantic.BaseModel):
    server: DBServer | DBFile
    cleanup: DatabaseCleanup


class DBServer(pydantic.BaseModel):
    username: str
    password: str
    location: str
    port: int
    database_name: str


class DBFile(pydantic.BaseModel):
    path: str


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

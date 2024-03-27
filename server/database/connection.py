# Fleet Protocol v2 HTTP API
# Copyright (C) 2023 BringAuto s.r.o.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from typing import Optional, Callable
from sqlalchemy import create_engine, Engine, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

_connection_source: Optional[Engine] = None


class CannotConnectToDatabase(Exception):
    pass


class ConnectionSourceNotSet(Exception):
    pass


class InvalidConnectionArguments(Exception):
    pass


class Base(DeclarativeBase):
    pass


class AdminBase(Base):
    __tablename__: str = "api_keys"
    __check_period_in_seconds__: int = 5
    __max_requests_per_period__: int = 5

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    key: Mapped[str] = mapped_column(String)


def get_connection_source() -> Engine:
    """Return the SQLAlchemy engine object used to connect to the database and
    raise exception if the engine object was not set yet.
    """
    global _connection_source
    if _connection_source is None:
        raise ConnectionSourceNotSet()
    else:
        assert isinstance(_connection_source, Engine)
        return _connection_source


def unset_connection_source() -> None:
    global _connection_source
    _connection_source = None



def set_db_connection(
    dblocation: str,
    username: str = "",
    password: str = "",
    db_name: str = "",
    after_connect: tuple[Callable[[], None], ...] = (),
) -> None:

    """Create SQLAlchemy engine object used to connect to the database.
    Set module-level variable _connection_source to the new engine object."""

    global _connection_source
    source = _new_connection_source(
        dialect="postgresql",
        dbapi="psycopg",
        dblocation=dblocation,
        username=username,
        password=password,
        db_name=db_name,
    )
    _connection_source = source
    assert _connection_source is not None
    create_all_tables(source)
    for foo in after_connect:
        foo()


def set_test_db_connection(dblocation: str = "", db_name: str = "") -> None:
    """Create test SQLAlchemy engine object used to connect to the database using SQLite.
    No username or password required.
    Set module-level variable _connection_source to the new engine object."""
    global _connection_source
    source = _new_connection_source(
        dialect="sqlite", dbapi="pysqlite", dblocation=dblocation, db_name=db_name
    )
    _connection_source = source
    assert _connection_source is not None
    create_all_tables(source)


def get_db_connection(
    dblocation: str, username: str = "", password: str = "", db_name: str = ""
) -> Engine | None:
    """Create SQLAlchemy engine object used to connect to the database.
    Do not modify module-level variable _connection_source."""
    source = _new_connection_source(
        dialect="postgresql",
        dbapi="psycopg",
        dblocation=dblocation,
        username=username,
        password=password,
        db_name=db_name,
    )
    return source


def get_test_db_connection(dblocation: str = "", db_name: str = "") -> Engine | None:
    """Create test SQLAlchemy engine object used to connect to the database using SQLite.
    No username or password required.
    Do not modify module-level variable _connection_source."""
    source = _new_connection_source(
        dialect="sqlite", dbapi="pysqlite", dblocation=dblocation, db_name=db_name
    )
    return source


def create_all_tables(source: Engine) -> None:
    Base.metadata.create_all(source)


def _new_connection_source(
    dialect: str,
    dbapi: str,
    dblocation: str,
    username: str = "",
    password: str = "",
    db_name: str = "",
    *args,
    **kwargs,
) -> Engine:

    try:
        url = _engine_url(dialect, dbapi, username, password, dblocation, db_name)
        engine = create_engine(url, *args, **kwargs)
        if engine is None:
            raise InvalidConnectionArguments(
                "Could not create new connection source ("
                f"{dialect},'+',{dbapi},://...{dblocation})"
            )
    except:
        raise InvalidConnectionArguments(
            "Could not create new connection source (" f"{dialect},'+',{dbapi},://...{dblocation})"
        )

    try:
        with engine.connect():
            pass
    except:
        raise CannotConnectToDatabase(
            "Could not connect to the database with the given connection parameters: \n"
            f"{url}\n\n"
            "Check the location, port number, username and password."
        )
    return engine


def _engine_url(
    dialect: str, dbapi: str, username: str, password: str, dblocation: str, db_name: str = ""
) -> str:
    if db_name != "":
        db_name = "/" + db_name

    if username != "" or password != "":
        user_info = username + ":" + password + "@"
    else:
        user_info = ""

    return ("").join([dialect, "+", dbapi, "://", user_info, dblocation, db_name])

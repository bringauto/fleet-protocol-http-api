from typing import Optional, Callable
import tenacity
import logging
import time

from sqlalchemy import create_engine, Engine, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import OperationalError

from server.logs import LOGGER_NAME


N_RETRIES = 3
RETRY_DELAY_SECONDS = 2


_connection_source: Optional[Engine] = None
_database_accessible: bool = False
_logger = logging.getLogger(LOGGER_NAME)


class DatabaseNotAccessible(Exception):
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
        t0 = time.monotonic()
        _test_connection_engine(_connection_source)
        elapsed_ms = (time.monotonic() - t0) * 1000
        if elapsed_ms > 50:
            _logger.warning("get_connection_source: _test_connection_engine took %.1f ms (>50 ms)", elapsed_ms)
        else:
            _logger.debug("get_connection_source: _test_connection_engine took %.1f ms", elapsed_ms)
        return _connection_source


@tenacity.retry(
    stop=tenacity.stop_after_attempt(N_RETRIES),
    wait=tenacity.wait_exponential_jitter(
        initial=RETRY_DELAY_SECONDS,
        max=5 * RETRY_DELAY_SECONDS,
        exp_base=1.5,
    ),
    reraise=True,
)
def _test_connection_engine(engine: Engine) -> None:
    global _database_accessible
    try:
        t0 = time.monotonic()
        with engine.begin() as _:
            pass
        elapsed_ms = (time.monotonic() - t0) * 1000
        if elapsed_ms > 10:
            _logger.warning("_test_connection_engine: engine.begin() took %.1f ms (>10 ms)", elapsed_ms)
        else:
            _logger.debug("_test_connection_engine: engine.begin() took %.1f ms", elapsed_ms)
        _database_accessible = True
        return
    except OperationalError as e:
        if _database_accessible:
            _logger.error("Lost connection to the database. Operational error: %s", e)
        _database_accessible = False
        raise DatabaseNotAccessible(
            "Could not connect to the database. Operational error: " + str(e)
        ) from e


def unset_connection_source() -> None:
    global _connection_source
    _connection_source = None


def set_db_connection(
    dblocation: str,
    port: int | str = "",
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
        dblocation=":".join((dblocation, str(port))),
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
        engine = create_engine(url, pool_pre_ping=True, *args, **kwargs)
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
        raise DatabaseNotAccessible(
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

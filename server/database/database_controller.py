from __future__ import annotations
from typing import ClassVar, Any
import dataclasses
import copy
import logging as _logging

from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import Integer, String, JSON, select, insert, delete, BigInteger, and_, or_
from sqlalchemy.exc import (
    IntegrityError as _IntegrityError,
    OperationalError as _OperationalError,
)
import psycopg

from server.database.connection import (
    DatabaseNotAccessible as _DatabaseNotAccessible,
)
from server.enums import MessageType  # type: ignore
from server.database.connection import (
    Base,
    get_connection_source as _get_connection_source,
    set_db_connection as _set_db_connection,
    set_test_db_connection as _set_test_db_connection,
)
from server.database.cache import (  # type: ignore
    add_car,
    add_device,
    connected_cars,
    clean_up_disconnected_cars_and_modules,
    remove_connected_device,
    clear_connected_cars as _clear_connected_cars,
)
from server.fleetv2_http_api.models.device_id import DeviceId  # type: ignore
from server.logs import LOGGER_NAME


_logger = _logging.getLogger(LOGGER_NAME)


@dataclasses.dataclass
class MessageBase(Base):
    """Object defining message table inside the database."""

    __tablename__: ClassVar[str] = "message"  # type: ignore
    _data_retention_period_in_seconds: ClassVar[int] = 10000
    __table_args__ = {"extend_existing": True}

    timestamp: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sent_order: Mapped[int] = mapped_column(Integer, primary_key=True, default=0)

    company_name: Mapped[str] = mapped_column(String, primary_key=True)
    car_name: Mapped[str] = mapped_column(String, primary_key=True)
    serialized_device_id: Mapped[str] = mapped_column(String, primary_key=True)

    module_id: Mapped[int] = mapped_column(Integer)
    device_type: Mapped[int] = mapped_column(Integer)
    device_role: Mapped[str] = mapped_column(String)
    device_name: Mapped[str] = mapped_column(String)

    message_type: Mapped[str] = mapped_column(String, primary_key=True)
    payload_encoding: Mapped[str] = mapped_column(String)
    payload_data: Mapped[dict] = mapped_column(JSON)

    @classmethod
    def data_retention_period_ms(cls) -> int:
        """Return the data retention period in milliseconds"""
        return cls._data_retention_period_in_seconds * 1000

    @classmethod
    def set_data_retention_period(cls, seconds: int) -> None:
        if isinstance(seconds, int) and seconds > 0:
            cls._data_retention_period_in_seconds = seconds

    @staticmethod
    def from_message(
        company_name: str, car_name: str, message: MessageDB, order: int = 0
    ) -> MessageBase:
        return MessageBase(
            timestamp=message.timestamp,
            sent_order=order,
            company_name=company_name,
            car_name=car_name,
            serialized_device_id=message.serialized_device_id,
            module_id=message.module_id,
            device_type=message.device_type,
            device_role=message.device_role,
            device_name=message.device_name,
            message_type=message.message_type,
            payload_encoding=message.payload_encoding,
            payload_data=message.payload_data,  # type: ignore
        )

    @staticmethod
    def from_messages(company_name: str, car_name: str, *messages: MessageDB) -> list[MessageBase]:
        bases: list[MessageBase] = list()
        for k in range(len(messages)):
            bases.append(
                MessageBase.from_message(company_name, car_name, message=messages[k], order=k)
            )
        return bases

    def to_message(self) -> MessageDB:
        return MessageDB(
            timestamp=self.timestamp,
            module_id=self.module_id,
            device_type=self.device_type,
            device_role=self.device_role,
            device_name=self.device_name,
            serialized_device_id=self.serialized_device_id,
            message_type=self.message_type,
            payload_encoding=self.payload_encoding,
            payload_data=self.payload_data,
        )


@dataclasses.dataclass
class MessageDB:
    """Object defining the structure of messages sent to and retrieved from the database."""

    timestamp: int
    serialized_device_id: str
    module_id: int
    device_type: int
    device_role: str
    device_name: str
    message_type: str
    payload_encoding: str
    payload_data: dict[str, str]


def set_message_retention_period(seconds: int) -> None:
    MessageBase.set_data_retention_period(seconds)


def set_db_connection(dblocation: str, username: str = "", password: str = "") -> None:
    _set_db_connection(
        dblocation=dblocation,
        username=username,
        password=password,
        after_connect=(load_available_devices_from_database,),
    )


def set_test_db_connection(dblocation: str) -> None:
    _set_test_db_connection(dblocation=dblocation)


def get_available_devices_from_database() -> None:
    _clear_connected_cars()
    load_available_devices_from_database()


def send_messages_to_database(
    company_name: str, car_name: str, *messages: MessageDB
) -> tuple[str, int]:
    """Send a list of messages to the database, returns number of succesfully sent messages (int)."""
    try:
        with _get_connection_source().begin() as conn:
            stmt = insert(MessageBase.__table__)  # type: ignore
            msg_base = MessageBase.from_messages(company_name, car_name, *messages)
            data_list = [msg.__dict__ for msg in msg_base]
            conn.execute(stmt, data_list)
            return _get_message_for_n_messages_succesfully_sent(len(messages)), 200
    except _IntegrityError:
        return (
            "Some of the messages are identical to those sent previously, including their timestamps.",
            400,
        )
    except _DatabaseNotAccessible:
        return "Database not accessible.", 503
    except Exception as e:
        return f"Internal server error : {e}.", 500


def _get_message_for_n_messages_succesfully_sent(number_of_sent_messages: int) -> str:
    if number_of_sent_messages == 1:
        return "1 message has been sent."
    else:
        return f"{number_of_sent_messages} messages have been sent."


def list_messages(
    company_name: str, car_name: str, message_type: tuple[str, ...], since: int = 0
) -> list[MessageDB]:  # noqa:
    """Return a list of messages of the given type, optionally filtered by the given parameters.
    If all is not None, then all messages of the given type are returned.

    Otherwise, if since is not None, then all messages of the given type with a timestamp
    less or equal to since are returned. Otherwise, the newest message is returned.
    """

    statuses: list[MessageDB] = list()
    with Session(_get_connection_source()) as session:
        table = MessageBase.__table__
        selection = select(MessageBase)
        selection = selection.where(or_(*[table.c.message_type == type for type in message_type]))
        selection = selection.where(
            and_(
                table.c.company_name == company_name,
                table.c.car_name == car_name,
                table.c.timestamp >= since,
            )
        ).order_by(table.c.timestamp.asc())
        result = session.execute(selection)
        for row in result:
            base: MessageBase = row[0]
            statuses.append(base.to_message())
        return statuses


def cleanup_device_commands_and_warn_before_future_commands(
    current_timestamp: int, company_name: str, car_name: str, serialized_device_id: str
) -> list[str]:
    """Remove all device commands assigned to a device before the first status was sent.

    All such commands ought to have timestamp less than or equal to the timestamp
    of the first status.

    If any commands have a timestamp greater than the timestamp of the first status,
    then return a warning.

    """
    table = MessageBase.__table__
    with _get_connection_source().begin() as conn:
        stmt = (
            delete(table)  # type: ignore
            .where(
                table.c.message_type == MessageType.COMMAND,
                table.c.company_name == company_name,
                table.c.car_name == car_name,
                table.c.serialized_device_id == serialized_device_id,
            )
            .returning(
                table.c.timestamp,
                table.c.company_name,
                table.c.car_name,
                table.c.serialized_device_id,
                table.c.payload_data,
            )
        )
        result = conn.execute(stmt)
        future_command_warnings: list[str] = []
        for row in result:
            if row[0] > current_timestamp:
                future_command_warnings.append(
                    future_command_warning(
                        timestamp=row[0],
                        company_name=row[1],
                        car_name=row[2],
                        serialized_device_id=row[3],
                        payload_data=row[4],
                    )
                )
        return future_command_warnings


def future_command_warning(
    timestamp: int, company_name: str, car_name: str, serialized_device_id: str, payload_data: Any
) -> str:
    """Construct a warning message for a command with a timestamp greater
    than the timestamp of the first status.
    """
    return (
        "Warning: Removing command existing before first status was sent, "
        "but with newer timestamp\n:"
        f"timestamp: {timestamp}, company:{company_name}, car:{car_name}, \
            device id:{serialized_device_id}, payload: {payload_data}."
    )


def remove_old_messages(current_timestamp: int) -> None:
    """Remove all messages with a timestamp older than the current timestamp
    minus the data retention period.
    """
    try:
        with _get_connection_source().begin() as conn:
            oldest_timestamp_to_be_kept = current_timestamp - MessageBase.data_retention_period_ms()
            stmt = delete(MessageBase.__table__).where(  # type: ignore
                MessageBase.__table__.c.timestamp < oldest_timestamp_to_be_kept
            )
            conn.execute(stmt)
        clean_up_disconnected_cars()
    except psycopg.errors.UndefinedTable:
        _logger.debug("The database table does not exist yet, no messages to clean up.")
    except _DatabaseNotAccessible:
        _logger.debug("Database is not accessible, do nothing")
    except _OperationalError as e:
        _logger.error(f"Cannot clean up old messages. Operational error: {e}")
    except Exception as e:
        _logger.error(f"Cannot clean up old messages. Error: {e}")


def clean_up_disconnected_cars() -> None:
    """Remove all car keys from the device_ids dictionary that do not have any modules.
    Then remove all companies that do not have any cars left.
    """
    device_dict = copy.deepcopy(connected_cars())
    for company in device_dict:
        for car in device_dict[company]:
            for module_id in device_dict[company][car].modules:
                _clean_up_disconnected_devices(company, car, module_id)
    clean_up_disconnected_cars_and_modules()


def _clean_up_disconnected_devices(company: str, car: str, module_id: int) -> None:
    """Remove all device ids from the device_ids dictionary that do not have any messages."""
    module_devices = connected_cars()[company][car].modules[module_id].device_ids.values()
    for device_id in module_devices:
        with Session(_get_connection_source()) as session:
            table = MessageBase.__table__
            select_stmt = select(MessageBase).where(
                table.c.message_type == MessageType.STATUS,
                table.c.company_name == company,
                table.c.car_name == car,
                table.c.module_id == module_id,
                table.c.device_type == device_id.type,
                table.c.device_role == device_id.role,
            )
            selection = session.execute(select_stmt)
            if selection.first() is None:
                remove_connected_device(company, car, device_id)


def deserialize_device_id(serialized_id: str) -> tuple[int, int, str]:
    """Split the serialized device id into its component parts."""
    module_id, device_type, device_role = serialized_id.split("_", 2)
    return int(module_id), int(device_type), device_role


def load_available_devices_from_database() -> None:
    with Session(_get_connection_source()) as session:
        stmt = select(MessageBase).where(MessageBase.message_type == MessageType.STATUS)
        result = session.execute(stmt)
        for row in result:
            base: MessageBase = row[0]
            device_id = DeviceId(
                module_id=base.module_id,
                type=base.device_type,
                role=base.device_role,
                name=base.device_name,
            )
            timestamp = base.timestamp
            add_car(base.company_name, base.car_name, timestamp)
            add_device(base.company_name, base.car_name, device_id)

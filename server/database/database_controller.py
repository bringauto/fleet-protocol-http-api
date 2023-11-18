from __future__ import annotations

from typing import Optional, List, ClassVar
import dataclasses
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import Integer, String, JSON, select, insert, BigInteger
from enums import MessageType
from database.device_ids import remove_device_id


_connection_source:Optional[Engine] = None


def connection_source()->Engine|None:
    return _connection_source


def get_connection_source()->Engine:
    """Return the SQLAlchemy engine object used to connect to the database and
    raise exception if the engine object was not set yet.
    """
    if isinstance(_connection_source, Engine): 
        return _connection_source
    else: 
        raise Connection_Source_Not_Set(_connection_source)


class Connection_Source_Not_Set(Exception): pass


def _new_connection_source(
    dialect:str, 
    dbapi:str, 
    dblocation:str, 
    username:str="", 
    password:str="", 
    *args,
    **kwargs
    )->Engine:

    url = ('').join([dialect,'+',dbapi,"://",username,":",password,"@",dblocation])
    return create_engine(url, *args, **kwargs)


def set_db_connection(
    dialect:str, 
    dbapi:str, 
    dblocation:str, 
    username:str="", 
    password:str="", 
    *args,
    **kwargs
    )->None:


    source = _new_connection_source(dialect, dbapi, dblocation, username, password, *args, **kwargs)
    global _connection_source
    _connection_source = source
    assert(_connection_source is not None)
    __create_all_tables(source)
    

def set_message_retention_period(seconds:int)->None:
    MessageBase.set_data_retention_period(seconds)


def unset_connection_source()->None:
    global _connection_source
    _connection_source = None


def __create_all_tables(source:Engine)->None:
    Base.metadata.create_all(source)


class Base(DeclarativeBase):  
    pass


@dataclasses.dataclass
class MessageBase(Base):
    """Object defining message table inside the database."""
    __tablename__:ClassVar[str] = "message"
    __data_retention_period_in_seconds:ClassVar[int] = 10000

    timestamp:Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sent_order:Mapped[int] = mapped_column(Integer, primary_key=True)

    company_name:Mapped[str] = mapped_column(String, primary_key=True)
    car_name:Mapped[str] = mapped_column(String, primary_key=True)

    module_id:Mapped[int] = mapped_column(Integer, primary_key=True)
    device_type:Mapped[int] = mapped_column(Integer, primary_key=True)
    device_role:Mapped[str] = mapped_column(String, primary_key=True)

    payload_type:Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_encoding:Mapped[int] = mapped_column(Integer)
    payload_data:Mapped[dict] = mapped_column(JSON)


    @classmethod
    @property
    def data_retention_period_s(cls)->int: 
        """Return the data retention period in seconds"""
        return cls.__data_retention_period_in_seconds
    
    @classmethod
    @property
    def data_retention_period_ms(cls)->int: 
        """Return the data retention period in milliseconds"""
        return cls.__data_retention_period_in_seconds*1000

    @classmethod
    def set_data_retention_period(cls, seconds:int)->None:
        cls.__data_retention_period_in_seconds = seconds
    
    @staticmethod
    def from_model(company_name:str, car_name:str, message:Message_DB, order:int=0)->MessageBase:
        return MessageBase(
            timestamp=message.timestamp,
            sent_order=order,

            company_name=company_name,
            car_name=car_name,

            module_id = message.module_id,
            device_type = message.device_type,
            device_role = message.device_role,
            payload_type = message.message_type, 
            payload_encoding=message.payload_encoding,
            payload_data=message.payload_data # type: ignore
        )

    @staticmethod
    def from_models(company_name:str, car_name:str, *models:Message_DB)->List[MessageBase]:
        bases:List[MessageBase] = list()
        for k in range(len(models)):
            bases.append(MessageBase.from_model(company_name, car_name, message = models[k], order=k))
        return bases

    def to_model(self)->Message_DB:
        return Message_DB(
            timestamp=self.timestamp,
            module_id=self.module_id,
            device_type=self.device_type,
            device_role=self.device_role,
            message_type=self.payload_type,
            payload_encoding=self.payload_encoding,
            payload_data=self.payload_data
        )
    

from typing import Dict
@dataclasses.dataclass
class Message_DB:
    """Object defining the structure of messages sent to and retrieved from the database."""
    timestamp:int
    module_id:int
    device_type:int
    device_role:str
    message_type:int
    payload_encoding:int
    payload_data:Dict[str,str]


def send_messages_to_database(company_name:str, car_name:str, *messages:Message_DB)->None: 
    with get_connection_source().begin() as conn:
        stmt = insert(MessageBase.__table__) # type: ignore
        msg_base = MessageBase.from_models(company_name, car_name, *messages)
        data_list = [msg.__dict__ for msg in msg_base]
        conn.execute(stmt, data_list)


from sqlalchemy import func, and_
def list_messages(
    company_name:str, 
    car_name:str, 
    message_type:int, 
    module_id:int,
    device_type:int,
    device_role:str,
    all:Optional[str]=None, 
    since:Optional[int]=None
    )->List[Message_DB]:  # noqa: 
    
    """Return a list of messages of the given type, optionally filtered by the given parameters.
    If all is not None, then all messages of the given type are returned.
    Otherwise, if since is not None, then all messages of the given type with a timestamp less than or equal to since are returned.
    Otherwise, the newest status or oldest command is returned.
    """
    
    statuses:List[Message_DB] = list()
    with Session(get_connection_source()) as session:
        table = MessageBase.__table__
        selection = select(MessageBase).where(table.c.payload_type == message_type)
        if all is not None:
            selection = selection.where(and_(
                table.c.company_name == company_name,
                table.c.car_name == car_name,
                table.c.module_id == module_id,
                table.c.device_type == device_type,
                table.c.device_role == device_role,
            ))
        elif since is not None:
            selection = selection.where(and_(
                table.c.company_name == company_name,
                table.c.car_name == car_name,
                table.c.module_id == module_id,
                table.c.device_type == device_type,
                table.c.device_role == device_role,
                table.c.timestamp <= since
            ))
        else:
            # return newest status or oldest command
            extreme_func = func.max if message_type==0 else func.min
            extreme_value = session.query(extreme_func(table.c.timestamp)).\
                where(
                    table.c.company_name == company_name,
                    table.c.car_name == car_name,
                    table.c.payload_type == message_type
                ).scalar()    
            selection = selection.where(table.c.timestamp == extreme_value)
            
        result = session.execute(selection)
        for row in result:
            base:MessageBase = row[0]
            statuses.append(base.to_model())
        return statuses
    

from sqlalchemy import delete
def cleanup_device_commands_and_warn_before_future_commands(
    current_timestamp:int, 
    company_name:str,
    car_name:str,
    module_id:int,
    device_type:int,
    device_role:str
    )->List[str]: 

    """Remove all device commands assigned to a device before the first status was sent.

    All such commands ought to have timestamp less than or equal to the timestamp of the first status.

    If any commands have a timestamp greater than the timestamp of the first status, then return a warning.

    """
    table = MessageBase.__table__
    with get_connection_source().begin() as conn: 
        stmt = delete(table).where( # type: ignore
            table.c.payload_type == MessageType.COMMAND_TYPE,
            table.c.company_name == company_name,
            table.c.car_name == car_name,   
            table.c.module_id == module_id,
            table.c.device_type == device_type,
            table.c.device_role == device_role,
        ).returning(
            table.c.timestamp,
            table.c.company_name,
            table.c.car_name,   
            table.c.module_id,
            table.c.device_type,
            table.c.device_role,
            table.c.payload_data
        )
        result = conn.execute(stmt)
        future_command_warnings:List[str] = []
        for row in result:
            if row[0]>current_timestamp: 
                future_command_warnings.append(future_command_warning(
                    timestamp=row[0], 
                    company_name=row[1], 
                    car_name=row[2], 
                    module_id=row[3],
                    device_type=row[4],
                    device_role=row[5],
                    payload_data=row[6]
                ))
        return future_command_warnings


from typing import Any
def future_command_warning(
    timestamp:int, 
    company_name:str, 
    car_name:str, 
    module_id:int, 
    device_type:int,
    device_role:str,
    payload_data:Any
    )->str:

    """Construct a warning message for a command with a timestamp greater 
    than the timestamp of the first status.
    """
    return "Warning: Removing command existing before first status was sent, " \
           "but with newer timestamp\n:" \
           f"timestamp: {timestamp}, company:{company_name}, car:{car_name}, module id:{module_id}, " \
           f"device type: {device_type}, device_role: {device_role}, payload: {payload_data}."


def remove_old_messages(current_timestamp:int)->None:  
    """Remove all messages with a timestamp older than the current timestamp 
    minus the data retention period.
    """
    with get_connection_source().begin() as conn: 
        oldest_timestamp_to_be_kept = current_timestamp - MessageBase.data_retention_period_ms
        stmt = delete(MessageBase.__table__).where( # type: ignore
            MessageBase.__table__.c.timestamp < oldest_timestamp_to_be_kept
        ) 
        conn.execute(stmt)
    clean_up_disconnected_cars()

    
from database.device_ids import device_ids, clean_up_disconnected_cars_and_modules

import copy
def clean_up_disconnected_cars()->None:
    """Remove all car keys from the device_ids dictionary that do not have any modules.
    Then remove all companies that do not have any cars left.
    """
    device_dict = copy.deepcopy(device_ids())
    for company in device_dict:
        for car in device_dict[company]:
            for module_id in device_dict[company][car]:
                __clean_up_disconnected_devices(company, car, module_id)
    clean_up_disconnected_cars_and_modules()          


def __clean_up_disconnected_devices(company:str, car:str, module_id:int)->None:
    """Remove all device ids from the device_ids dictionary that do not have any messages."""
    module_devices = device_ids()[company][car][module_id]
    for serialized_device_id in module_devices:
        _, device_type, device_role = _deserialize_device_id(serialized_device_id)
        with Session(get_connection_source()) as session: 
            table = MessageBase.__table__
            select_stmt = select(MessageBase).where(
                table.c.payload_type == MessageType.STATUS_TYPE,
                table.c.company_name == company,
                table.c.car_name == car,
                table.c.module_id == module_id,
                table.c.device_type == device_type,
                table.c.device_role == device_role,
            )
            selection = session.execute(select_stmt)
            if selection.first() is None:
                remove_device_id(company, car, module_id, serialized_device_id)


from typing import Tuple
def _deserialize_device_id(serialized_id:str)->Tuple[int,int,str]:
    """Split the serialized device id into its component parts.
    """
    module_id, device_type, device_role = serialized_id.split("_",2)
    return int(module_id), int(device_type), device_role

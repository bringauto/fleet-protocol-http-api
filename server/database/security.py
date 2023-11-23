from __future__ import annotations


from typing import Literal, ClassVar, List

import dataclasses
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session
from database.database_connection import Base, get_connection_source


class ClientBase(Base):
    __tablename__:ClassVar[str] = "clients"
    __check_period_in_seconds__:ClassVar[int] = 5
    __max_requests_per_period__:ClassVar[int] = 5

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String)
    key:Mapped[str] = mapped_column(String)
    type:Mapped[str] = mapped_column(String)
    counter:Mapped[int] = mapped_column(Integer, default=0)

    __mapper_args__ = {
        'polymorphic_identity':'client',
        'polymorphic_on':type
    }


ClientType = Literal["visitor", "operator"]

    
__loaded_clients:List[Client_DB] = []

def clear_loaded_clients()->None:
    global __loaded_clients
    __loaded_clients.clear()


@dataclasses.dataclass
class Client_DB:
    id:int
    name:str
    key:str



class VisitorBase(ClientBase):
    __tablename__:ClassVar[str] = "visitors"
    id: Mapped[int] = mapped_column(ForeignKey("clients"), primary_key=True)
    name:Mapped[str] = mapped_column(String)
    key:Mapped[str] = mapped_column(String)

    __mapper_args__ = {
        'polymorphic_identity':'visitor',
    }


class OperatorBase(ClientBase):
    __tablename__:ClassVar[str] = "operators"
    id: Mapped[int] = mapped_column(ForeignKey("clients"), primary_key=True)
    name:Mapped[str] = mapped_column(String)
    key:Mapped[str] = mapped_column(String)

    __mapper_args__ = {
        'polymorphic_identity':'operator',
    }


from typing import Dict, Type
__client_types:Dict[ClientType, Type[ClientBase]] = {
    "visitor":VisitorBase,
    "operator":OperatorBase
}


from sqlalchemy import select
def add_client(name:str, client_type:ClientType)->str:
    if client_type not in __client_types: 
        raise ValueError(f"Invalid client type: {client_type}")
    
    with Session(get_connection_source()) as session:
        key = __generate_key()
        client = __client_types[client_type](name=name, key=key)
        session.add(client)
        session.commit()
        return key


from sqlalchemy import select
def get_client(key:str, client_type:str)->Client_DB|None:
    if client_type not in __client_types: return None

    global __loaded_clients
    for client in __loaded_clients:
        if client.key == key:
            return client
    
    with Session(get_connection_source()) as session:
        client_base_class = __client_types[client_type]
        result = session.execute(select(client_base_class).where(client_base_class.key==key)).first()

        if result is None: return None
        else:
            clientbase:ClientBase = result[0]
            client = Client_DB(id=clientbase.id, name=clientbase.name, key=clientbase.key)
            __loaded_clients.append(client)
            return client
    

from sqlalchemy import Select, func

def client_selection(key:str, type:ClientType)->Select:
    return select(__client_types[type]).where(__client_types[type].key==key)


from sqlalchemy import func
def number_of_clients(type:ClientType)->int:
    with Session(get_connection_source()) as session:
        return session.query(func.count(__client_types[type].__table__.c.id)).scalar()


import random
import string
def __generate_key()->str:
    return '1234567890'
    # return ''.join(random.choice(string.ascii_letters) for _ in range(30))


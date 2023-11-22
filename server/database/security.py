from __future__ import annotations


from typing import Literal, ClassVar, List

import dataclasses
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, Session
from database.database_connection import Base, get_connection_source


Role = Literal["visitor", "operator"]


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


class VisitorBase(ClientBase):
    __tablename__:ClassVar[str] = "visitors"
    id: Mapped[int] = mapped_column(ForeignKey("clients"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'visitor',
    }


class OperatorBase(ClientBase):
    __tablename__:ClassVar[str] = "operators"
    id: Mapped[int] = mapped_column(ForeignKey("clients"), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'operator',
    }
    

__clients:List[Client_DB] = []


@dataclasses.dataclass
class Client_DB:
    id:int
    name:str
    key:str


from sqlalchemy import select
def get_client(key:str, client_type:str)->Client_DB|None:
    global __clients
    for client in __clients:
        if client.key == key:
            return client
    
    with Session(get_connection_source()) as session:
        if client_type == "visitor":
            result = session.execute(visitor_selection(key)).first()
        elif client_type == "operator":
            result = session.execute(operator_selection(key)).first()
        else: 
            result = None

        if result is None: 
            return None
        else:
            clientbase:ClientBase = result[0]
            client = Client_DB(id=clientbase.id, name=clientbase.name, key=clientbase.key)
            __clients.append(client)
            return client
            

from sqlalchemy import select
def add_client(name:str, type:Role)->str:
    with Session(get_connection_source()) as session:
        key = __generate_key()
        if type == "visitor":
            client = VisitorBase(name=name, key=key)
        elif type == "operator":
            client = OperatorBase(name=name, key=key)
        else:
            raise ValueError(f"Invalid client type: {type}")
        session.add(client)
        session.commit()
        return key
    

from sqlalchemy import Select
def visitor_selection(key:str)->Select:
    return select(VisitorBase).where(VisitorBase.key==key)


def operator_selection(key:str)->Select:
    return select(OperatorBase).where(OperatorBase.key==key)


from sqlalchemy import func
def number_of_visitors()->int:
    with Session(get_connection_source()) as session:
        return session.query(func.count(VisitorBase.__table__.c.id)).scalar()
    
def number_of_operators()->int:
    with Session(get_connection_source()) as session:
        return session.query(func.count(OperatorBase.__table__.c.id)).scalar()


import random
import string
def __generate_key()->str:
    return ''.join(random.choice(string.ascii_letters) for _ in range(30))


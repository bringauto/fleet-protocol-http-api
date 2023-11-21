from typing import Literal, ClassVar

import dataclasses
import datetime
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

    def get_key(self)->str|None:
        self.__reset_counter_if_period_passed()
        self.counter += 1
        if self.counter>self.__max_requests_per_period__:
            return None
        else:
            return self.key
        
    def __reset_counter_if_period_passed(self)->None:
        curr_time = datetime.datetime.now()
        if curr_time - self.last_time >= datetime.timedelta(seconds=self.__check_period_in_seconds__):
            self.last_time = curr_time
            self.counter = 0

    class TooManyRequests(Exception): pass



class VisitorBase(ClientBase):
    __tablename__:ClassVar[str] = "visitors"
    id: Mapped[int] = mapped_column(ForeignKey("clients"), primary_key=True)
    name:Mapped[str] = mapped_column(String)
    key:Mapped[str] = mapped_column(String)


class OperatorBase(ClientBase):
    __tablename__:ClassVar[str] = "operators"
    id: Mapped[int] = mapped_column(ForeignKey("clients"), primary_key=True)
    name:Mapped[str] = mapped_column(String, )
    key:Mapped[str] = mapped_column(String)
    

@dataclasses.dataclass(frozen=True)
class Client_DB:
    id:int
    name:str
    key:str


from sqlalchemy import select
def get_client(key:str, client_type:str)->Client_DB|None:
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
            client:ClientBase = result[0]
            return Client_DB(id=client.id, name=client.name, key=client.key)
        

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
    return '1234567890'
    # return ''.join(random.choice(string.ascii_letters) for i in range(20))


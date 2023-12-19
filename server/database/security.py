from __future__ import annotations
from typing import ClassVar, List

import dataclasses
from sqlalchemy import String, Integer, Engine
from sqlalchemy.orm import Mapped, mapped_column, Session
from database.connection import Base, get_connection_source


class AdminBase(Base):
    __tablename__:ClassVar[str] = "api_keys"
    __check_period_in_seconds__:ClassVar[int] = 5
    __max_requests_per_period__:ClassVar[int] = 5

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    name:Mapped[str] = mapped_column(String)
    key:Mapped[str] = mapped_column(String)


__loaded_admins:List[Admin_DB] = []


def clear_loaded_admins()->None:
    global __loaded_admins
    __loaded_admins.clear()


def get_loaded_admins()->List[Admin_DB]:
    return __loaded_admins.copy()


@dataclasses.dataclass
class Admin_DB:
    id:int
    name:str
    key:str


from typing import Optional
from sqlalchemy import select
def add_admin_key(name:str, connection_source:Optional[Engine]=None)->str:
    """Add an admin to the database and return the key."""
    if connection_source is None: connection_source = get_connection_source()
    __create_admin_table_if_it_does_not_exist(connection_source)
    with Session(connection_source) as session:
        existing_admin = session.query(AdminBase).filter(AdminBase.name==name).first()
        if existing_admin is not None: 
            return __admin_already_exists_msg(existing_admin.name)
        else:
            key = __generate_key()
            admin = AdminBase(name=name, key=key)
            session.add(admin)
            session.commit()
            return __admin_added_msg(name, key)
    
        
def __admin_added_msg(name:str, key:str)->str:
    return f"Admin '{name}' added with key '{key}'."
        

def __admin_already_exists_msg(name:str)->str:
    return f"Admin with name '{name}' already exists."


def __create_admin_table_if_it_does_not_exist(connection_source:Engine)->None:
    with connection_source.connect() as connection:
        if not connection_source.dialect.has_table(connection, AdminBase.__tablename__):
            AdminBase.metadata.create_all(connection_source)


def get_admin(key:str)->Admin_DB|None:
    loaded_admins  = get_loaded_admins()
    for admin in loaded_admins:
        if admin.key == key:
            return admin
    
    source = get_connection_source()
    if source is None: return None

    __create_admin_table_if_it_does_not_exist(source)

    with Session(get_connection_source()) as session:
        result = session.execute(select(AdminBase).where(AdminBase.key==key)).first()
        if result is None: return None
        else:
            admin_base:AdminBase = result[0]
            admin = Admin_DB(id=admin_base.id, name=admin_base.name, key=admin_base.key)
            __loaded_admins.append(admin)
            return admin


from sqlalchemy import Select, func

def admin_selection(key:str)->Select:
    return select(AdminBase).where(AdminBase.key==key)


from sqlalchemy import func
def number_of_admin_keys(connection:Engine|None = None)->int:
    if connection is None: connection = get_connection_source()
    with Session(connection) as session:
        return session.query(func.count(AdminBase.__table__.c.id)).scalar()


import random
import string
def __generate_key()->str: # pragma: no cover
    return ''.join(random.choice(string.ascii_letters) for _ in range(30))


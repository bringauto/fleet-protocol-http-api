from typing import Optional


from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase


_connection_source = Optional[Engine]


def connection_source()->Engine:
    if _connection_source is None: raise Connection_Source_Not_Set
    else: 
        return _connection_source


class Connection_Source_Not_Set(Exception): pass


class Base(DeclarativeBase):  
    pass


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


def set_connection_source(
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
    Base.metadata.create_all(source)
    

def unset_connection_source()->None:
    global _connection_source
    _connection_source = None
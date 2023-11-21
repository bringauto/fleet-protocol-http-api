from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase


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
    

def unset_connection_source()->None:
    global _connection_source
    _connection_source = None


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
    

def __create_all_tables(source:Engine)->None:
    Base.metadata.create_all(source)


class Base(DeclarativeBase):  
    pass

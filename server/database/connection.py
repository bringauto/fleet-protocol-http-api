from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase


_connection_source:Optional[Engine] = None


def get_connection_source()->Engine:
    """Return the SQLAlchemy engine object used to connect to the database and
    raise exception if the engine object was not set yet.
    """
    if _connection_source is None: 
        raise Connection_Source_Not_Set()
    else:
        assert isinstance(_connection_source, Engine)
        return _connection_source

    

def unset_connection_source()->None:
    global _connection_source, _connection_data
    _connection_source = None
    _connection_data = None


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


from typing import Callable, Tuple
def set_db_connection(
    dialect:str, 
    dbapi:str, 
    dblocation:str, 
    username:str="", 
    password:str="", 
    after_connect:Tuple[Callable[[], None],...] = (),
    )->None:

    global _connection_source
    source = _new_connection_source(dialect, dbapi, dblocation, username, password)
    _connection_source = source
    assert(_connection_source is not None)
    __create_all_tables(source)

    for foo in after_connect: foo()


def __create_all_tables(source:Engine)->None:
    Base.metadata.create_all(source)


class Base(DeclarativeBase):  
    pass

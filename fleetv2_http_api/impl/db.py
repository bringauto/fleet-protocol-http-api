from typing import Optional


from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase


_connection_source = Optional[Engine]


def connection_source()->Engine:
    if isinstance(_connection_source, Engine): 
        return _connection_source
    else: 
        raise Connection_Source_Not_Set


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


from fleetv2_http_api.models.connect_to_database_request import ConnectToDatabaseRequest

def connect_to_database(body=None, *args, **kwargs)->None:
    rq = body
    if rq is not None:
        set_connection_source(
            dialect=rq["dialect"], 
            dbapi=rq["dbapi"], 
            dblocation=rq["location"],
            username=rq["username"],
            password=rq["password"]
        )
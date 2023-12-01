# Fleet Protocol v2 HTTP API 
# Copyright (C) 2023 BringAuto s.r.o.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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
    engine = create_engine(url, *args, **kwargs)
    if engine is None: 
        raise Exception("Could not create connection source")
    return engine


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

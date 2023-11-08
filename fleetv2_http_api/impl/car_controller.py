from __future__ import annotations


from sqlalchemy import create_engine, insert, select, Engine
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
import dataclasses


from typing import List, ClassVar
from ..controllers.car_controller import Car


def new_connection_source(
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


from typing import Optional
_connection_source = Optional[Engine]


def set_connection_source(source:Engine)->None:
    global _connection_source
    _connection_source = source
    Base.metadata.create_all(source)


class Base(DeclarativeBase):  
    pass


@dataclasses.dataclass
class CarBase(Base):
    __tablename__:ClassVar[str] = "car"
    owner:Mapped[str] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(primary_key=True)

    @staticmethod
    def from_model(model:Car)->CarBase:
        return CarBase(owner=model.company_name, name=model.car_name)
    @staticmethod
    def to_model(base:CarBase)->Car:
        return Car(car_name=base.name, company_name=base.owner)



def cars_available()->List[Car]:  # noqa: E501
    with Session(_connection_source ) as session:
        result = session.execute(select(CarBase))
        cars:List[Car] = list()
        for row in result:
            carbase = row[0]
            cars.append(CarBase.to_model(carbase))
        return cars


def add_car(car:Car)->None:
    item = CarBase.from_model(car)
    with _connection_source.begin() as conn:
        stmt = insert(CarBase.__table__)
        conn.execute(stmt, [item.__dict__])
    

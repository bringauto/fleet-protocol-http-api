from __future__ import annotations


from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
import dataclasses


from typing import List, ClassVar
from ..controllers.car_controller import Car


engine = create_engine("sqlite+pysqlite:///:memory:")


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


Base.metadata.create_all(engine)


def cars_available()->List[Car]:  # noqa: E501
    with Session(engine) as session:
        result = session.execute(select(CarBase))
        cars:List[Car] = list()
        for row in result:
            carbase = row[0]
            cars.append(CarBase.to_model(carbase))
        return cars


def add_car(car:Car)->None:
    item = CarBase.from_model(car)
    with engine.begin() as conn:
        stmt = insert(CarBase.__table__)
        conn.execute(stmt, [item.__dict__])
    

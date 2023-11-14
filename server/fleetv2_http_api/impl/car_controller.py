from __future__ import annotations


from typing import List, ClassVar
import dataclasses

from sqlalchemy import select
from sqlalchemy.orm import Session, Mapped, mapped_column
from database.database_controller import Base, connection_source


from ..controllers.car_controller import Car


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

 
def cars_available()->List[Car]:
    with Session(connection_source()) as session:
        result = session.execute(select(CarBase))
        cars:List[Car] = list()
        for row in result:
            carbase = row[0]
            cars.append(CarBase.to_model(carbase))
        return cars


    

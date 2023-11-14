from __future__ import annotations


from typing import ClassVar
import dataclasses

from sqlalchemy.orm import Mapped, mapped_column
from database.database_controller import Base


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

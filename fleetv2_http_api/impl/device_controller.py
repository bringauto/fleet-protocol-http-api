from __future__ import annotations


from typing import ClassVar, List, Optional
import connexion
import dataclasses
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import insert, delete, select
from sqlalchemy import String, Integer, JSON, Enum

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device import Message, DeviceId
from fleetv2_http_api.impl.db import connection_source, Base


import enum


@dataclasses.dataclass
class MessageBase(Base):
    __tablename__:ClassVar[str] = "device"
    timestamp:Mapped[int] = mapped_column(primary_key=True)

    module_id:Mapped[int] = mapped_column(primary_key=True)
    device_type:Mapped[int] = mapped_column(primary_key=True)
    device_role:Mapped[str] = mapped_column(primary_key=True)
    device_name:Mapped[str] = mapped_column()

    payload_type:Mapped[int] = mapped_column(Integer)
    payload_encoding:Mapped[str] = mapped_column(String)
    payload_data:Mapped[dict] = mapped_column(JSON)

    @staticmethod
    def from_model(model:Message)->MessageBase:
        return MessageBase(
            timestamp=model.timestamp,
            module_id = model.id.module_id,
            device_type = model.id.type,
            device_role = model.id.role,
            device_name = model.id.name,
            payload_type = model.payload.type,  # type: ignore
            payload_encoding=model.payload.encoding,
            payload_data=model.payload.data # type: ignore
        )

    def to_model(self)->Message:
        return Message(
            timestamp=self.timestamp,
            id = DeviceId(
                module_id=self.module_id, 
                type=self.device_type, 
                role=self.device_role, 
                name=self.device_name
            ),
            payload=Payload(self.payload_type, self.payload_encoding, self.payload_data)
        )
    

def add_msg(*messages:Message)->None: 
    with connection_source().begin() as conn:
        stmt = insert(MessageBase.__table__) # type: ignore
        msg_base = [MessageBase.from_model(msg).__dict__ for msg in messages]
        conn.execute(stmt, msg_base)


def devices_available(module_id:Optional[int]=None)->List[DeviceId]:  # noqa: E501
    """devices_available

    Returns list of available devices for the whole car or a single module. # noqa: E501

    :param module_id: An Id of module.
    :type module_id: dict | bytes

    :rtype: Union[List[Device], Tuple[List[Device], int], Tuple[List[Device], int, Dict[str, str]]
    """
    # if connexion.request.is_json:
    #     module_id =  object.from_dict(connexion.request.get_json())  # noqa: E501
    devices:List[DeviceId] = list()
    with Session(connection_source()) as session:
        if module_id is not None:
            result = session.execute(select(MessageBase).where(MessageBase.__table__.c.module_id == module_id))
        else:
            result = session.execute(select(MessageBase))
        for row in result:
            devicebase:MessageBase = row[0]
            devices.append(devicebase.to_model().id)
    
    if module_id is not None and devices==[]: 
        return [], 404 # type: ignore
    else:
        return devices


def list_commands(device_id:DeviceId, all=None, since=None):  # noqa: E501
    """list_commands

    Returns list of the Device Commands. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: int
    :param company_name: Name of the company operating/running the car
    :type company_name: str
    :param car_name: Name of the the car
    :type car_name: str
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int

    :rtype: Union[List[Payload], Tuple[List[Payload], int], Tuple[List[Payload], int, Dict[str, str]]
    """
    commands:List[Message] = list()
    with Session(connection_source()) as session:
        result = session.execute(select(MessageBase).where(MessageBase.__table__.c.payload_type == 1))
        for row in result:
            base:MessageBase = row[0]
            commands.append(base.to_model())
        return commands


def list_statuses(device_id:DeviceId, all=None, since=None)->List[Message]:  # noqa: E501
    """list_statuses

    It returns list of the Device Statuses. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: int
    :param company_name: Name of the company operating/running the car
    :type company_name: str
    :param car_name: Name of the the car
    :type car_name: str
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int

    :rtype: Union[List[Payload], Tuple[List[Payload], int], Tuple[List[Payload], int, Dict[str, str]]
    """
    statuses:List[Message] = list()
    with Session(connection_source()) as session:
        result = session.execute(select(MessageBase).where(MessageBase.__table__.c.payload_type == 0))
        for row in result:
            base:MessageBase = row[0]
            statuses.append(base.to_model())
        return statuses


def send_commands(device_id, all=None, since=None, payload=None):  # noqa: E501
    """send_commands

    It adds new device Commands. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: int
    :param company_name: Name of the company operating/running the car
    :type company_name: str
    :param car_name: Name of the the car
    :type car_name: str
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int
    :param payload: Commands to be executed by the device.
    :type payload: list | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        payload = [Payload.from_dict(d) for d in connexion.request.get_json()]  # noqa: E501
    return 'do some magic!'


def send_statuses(device_id, all=None, since=None):  # noqa: E501
    """send_statuses

    Add statuses received from the Device. # noqa: E501

    :param device_id: The Id of the Device.
    :type device_id: int
    :param company_name: Name of the company operating/running the car
    :type company_name: str
    :param car_name: Name of the the car
    :type car_name: str
    :param all: If set, the method returns a complete history of statuses/commands.
    :type all: bool
    :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
    :type since: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'

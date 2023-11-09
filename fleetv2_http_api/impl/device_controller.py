from __future__ import annotations


from typing import ClassVar, List, Optional
import dataclasses
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import insert, select
from sqlalchemy import String, Integer, JSON

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device import Message, DeviceId
from fleetv2_http_api.impl.db import connection_source, Base



from time import time as __time
def timestamp()->int: return int(__time()*1000)


@dataclasses.dataclass
class MessageBase(Base):
    __tablename__:ClassVar[str] = "device"
    timestamp:Mapped[int] = mapped_column(primary_key=True, nullable=False)

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

def devices_available(module_id:Optional[int]=None)->List[DeviceId]:  # noqa: E501
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
    return __list_messages(1, device_id, all, since)


def list_statuses(device_id:DeviceId, all=None, since:Optional[int]=None)->List[Message]:  # noqa: E501
    return __list_messages(0, device_id, all, since)
    

from sqlalchemy import func, and_
def __list_messages(type:int, device_id:DeviceId, all=None, since:Optional[int]=None)->List[Message]:  # noqa: E501
    statuses:List[Message] = list()
    with Session(connection_source()) as session:
        query = select(MessageBase)
        if all is not None:
            query = query.where(MessageBase.__table__.c.payload_type == type)
        elif since is not None:
            query = query.where(and_(
                MessageBase.__table__.c.payload_type == type,
                MessageBase.__table__.c.timestamp <= since
            ))
        else:
            query = \
                query.where(MessageBase.__table__.c.payload_type == type)\
                .group_by(MessageBase.timestamp)\
                .having(func.max(MessageBase.timestamp))
        
        result = session.execute(query)
        for row in result:
            base:MessageBase = row[0]
            statuses.append(base.to_model())
        return statuses


def send_commands(device_id, all=None, since=None, payload:List[Payload]=list()):  # noqa: E501
    msgs = [Message(timestamp=timestamp(), id=device_id, payload=p) for p in payload]
    _add_msg(*msgs)


def send_statuses(device_id:DeviceId, all=None, since=None, payload:List[Payload]=list()):  # noqa: E501
    msgs = [Message(timestamp=timestamp(), id=device_id, payload=p) for p in payload]
    _add_msg(*msgs)


def _add_msg(*messages:Message)->None: 
    with connection_source().begin() as conn:
        stmt = insert(MessageBase.__table__) # type: ignore
        msg_base = [MessageBase.from_model(msg).__dict__ for msg in messages]
        conn.execute(stmt, msg_base)

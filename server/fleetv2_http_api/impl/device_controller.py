from __future__ import annotations


from typing import ClassVar, List, Optional
import dataclasses
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import insert, select
from sqlalchemy import String, Integer, JSON

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Message
from database_controller import connection_source, Base



DATA_RETENTION_PERIOD_IN_MS = 3600000 # 1 hour

from time import time as __time
def timestamp()->int: 
    """Timestamp in milliseconds."""
    return int(__time()*1000)


@dataclasses.dataclass
class MessageBase(Base):
    __tablename__:ClassVar[str] = "message"
    timestamp:Mapped[int] = mapped_column(primary_key=True)
    sent_order:Mapped[int] = mapped_column(primary_key=True)

    module_id:Mapped[int] = mapped_column(primary_key=True)
    device_type:Mapped[int] = mapped_column(primary_key=True)
    device_role:Mapped[str] = mapped_column(primary_key=True)
    device_name:Mapped[str] = mapped_column()

    payload_type:Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_encoding:Mapped[str] = mapped_column(String)
    payload_data:Mapped[dict] = mapped_column(JSON)
    
    @staticmethod
    def from_model(model:Message, order:int=0)->MessageBase:
        return MessageBase(
            timestamp=model.timestamp,
            sent_order=order,
            module_id = model.id.module_id,
            device_type = model.id.type,
            device_role = model.id.role,
            device_name = model.id.name,
            payload_type = model.payload.type, 
            payload_encoding=model.payload.encoding,
            payload_data=model.payload.data # type: ignore
        )

    @staticmethod
    def from_models(*models:Message)->List[MessageBase]:
        bases:List[MessageBase] = list()
        for k in range(len(models)):
            bases.append(MessageBase.from_model(models[k], k))
        return bases

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
    

@dataclasses.dataclass
class DeviceBase(Base):
    __tablename__:ClassVar[str] = "device"

    module_id:Mapped[int] = mapped_column(primary_key=True)
    device_type:Mapped[int] = mapped_column(primary_key=True)
    device_role:Mapped[str] = mapped_column(primary_key=True)
    device_name:Mapped[str] = mapped_column()

    @staticmethod
    def from_model(model:DeviceId)->DeviceBase:
        return DeviceBase(
            module_id=model.module_id,
            device_type=model.type,
            device_role=model.role,
            device_name=model.name
        ) # type: ignore

    def to_model(self)->DeviceId:
        return DeviceId(
            module_id=self.module_id, 
            type=self.device_type, 
            role=self.device_role, 
            name=self.device_name
        )


from typing import Dict
def add_device(company_name:str, car_name:str, body:Optional[Dict]=None)->None: 
    if body is None: return
    else:
        deviceid = DeviceId.from_dict(body)
        item = DeviceBase.from_model(deviceid)
        with connection_source().begin() as conn:
            stmt = insert(DeviceBase.__table__) # type: ignore
            conn.execute(stmt, [item.__dict__])


def available_devices(company_name:str, car_name:str, module_id:Optional[int]=None)->List[DeviceId]:  # noqa: E501

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
    _remove_old_messages(timestamp())
    return __list_messages(1, device_id, all, since)


def list_statuses(device_id:DeviceId, all=None, since:Optional[int]=None)->List[Message]:  # noqa: E501
    _remove_old_messages(timestamp())
    return __list_messages(0, device_id, all, since)


from sqlalchemy import func, and_
def __list_messages(type:int, device_id:DeviceId, all=None, since:Optional[int]=None)->List[Message]:  # noqa: E501
    statuses:List[Message] = list()
    with Session(connection_source()) as session:
        table = MessageBase.__table__
        selection = select(MessageBase).where(table.c.payload_type == type)
        if all is not None:
            selection = selection.where(and_(
                table.c.module_id == device_id.module_id,
                table.c.device_type == device_id.type,
                table.c.device_role == device_id.role,
            ))
        elif since is not None:
            selection = selection.where(and_(
                table.c.module_id == device_id.module_id,
                table.c.device_type == device_id.type,
                table.c.device_role == device_id.role,
                table.c.timestamp <= since
            ))
        else:
            # return newest status or oldest command
            extreme_func = func.max if type==0 else func.min
            extreme_value = session.query(extreme_func(table.c.timestamp)).\
                where(table.c.payload_type == type).scalar()    
            selection = selection.where(table.c.timestamp == extreme_value)
            
        result = session.execute(selection)
        for row in result:
            base:MessageBase = row[0]
            statuses.append(base.to_model())
        return statuses


def send_commands(device_id, payload:List[Payload]=list()):  # noqa: E501
    tstamp = timestamp()
    _remove_old_messages(tstamp)
    msgs = [Message(timestamp=tstamp, id=device_id, payload=p) for p in payload]
    _add_msg(*msgs)


def send_statuses(device_id:DeviceId, payload:List[Payload]=list()):  # noqa: E501
    tstamp = timestamp()
    _remove_old_messages(tstamp)
    msgs = [Message(timestamp=tstamp, id=device_id, payload=p) for p in payload]
    _add_msg(*msgs)


def _add_msg(*messages:Message)->None: 
    with connection_source().begin() as conn:
        stmt = insert(MessageBase.__table__) # type: ignore
        msg_base = MessageBase.from_models(*messages)
        data_list = [msg.__dict__ for msg in msg_base]
        conn.execute(stmt, data_list)

def _count_currently_stored_messages()->int:
    with Session(connection_source()) as session:
        return session.query(MessageBase).count()

from sqlalchemy import delete
def _remove_old_messages(current_timestamp:int)->None:  
    with connection_source().begin() as conn: 
        oldest_timestamp_to_be_kept = current_timestamp-DATA_RETENTION_PERIOD_IN_MS
        stmt = delete(MessageBase.__table__).where( # type: ignore
            MessageBase.__table__.c.timestamp < oldest_timestamp_to_be_kept
        ) 
        conn.execute(stmt)
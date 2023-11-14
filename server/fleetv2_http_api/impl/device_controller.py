from __future__ import annotations


from typing import ClassVar, List, Optional, Tuple
import dataclasses
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import insert, select
from sqlalchemy import String, Integer, JSON

from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Message
from fleetv2_http_api.impl.car_controller import Car
from database.database_controller import connection_source, Base, timestamp, DATA_RETENTION_PERIOD_IN_MS
from database.device_ids import store_device_id_if_new, device_ids


    
def available_cars()->List[str]:
    return list(device_ids().keys())


def available_devices(company_name:str, car_name:str, module_id:Optional[int]=None)->List[str]:  # noqa: E501
    car = _serialized_car_info(company_name, car_name)
    if car not in device_ids(): 
        return [], 404 # type: ignore
    if module_id is None: 
        return __all_available_devices(car)
    else: 
        return __available_devices_for_module(car, module_id)


def list_commands(device_id:DeviceId, all=None, since=None):  # noqa: E501
    return __list_messages(1, device_id, all, since)


def list_statuses(device_id:DeviceId, all=None, since:Optional[int]=None)->List[Message]:  # noqa: E501
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


def send_commands(company_name:str, car_name:str, device_id:DeviceId, payload:List[Payload]=list())->Tuple[str, int]:  # noqa: E501
    car = _serialized_car_info(company_name, car_name)
    if car not in device_ids():
        return "", 404
    elif device_id.module_id not in device_ids()[car]:
        return "", 404
    else:
        tstamp = timestamp()
        _remove_old_messages(tstamp)
        commands = [Message(timestamp=tstamp, id=device_id, payload=p) for p in payload]
        __send_messages_to_database(company_name, car_name, *commands)


def send_statuses(company_name:str, car_name:str, device_id:DeviceId, payload:List[Payload]=list())->Tuple[str,int]:  # noqa: E501
    tstamp = timestamp()
    statuses:List[Message] = list()
    for p in payload: 
        statuses.append(Message(tstamp, device_id, p))
    __send_messages_to_database(company_name, car_name, *statuses)
    store_device_id_if_new(
        car_info = _serialized_car_info(company_name, car_name), 
        module_id = device_id.module_id, 
        serialized_device_id = _serialized_device_id(device_id)
    )
    return "", 200


def __send_messages_to_database(company_name:str, car_name:str, *messages:Message)->None: 
    with connection_source().begin() as conn:
        stmt = insert(MessageBase.__table__) # type: ignore
        msg_base = MessageBase.from_models(company_name, car_name, *messages)
        data_list = [msg.__dict__ for msg in msg_base]
        conn.execute(stmt, data_list)


from sqlalchemy import delete
def _remove_old_messages(current_timestamp:int)->None:  
    with connection_source().begin() as conn: 
        oldest_timestamp_to_be_kept = current_timestamp-DATA_RETENTION_PERIOD_IN_MS
        stmt = delete(MessageBase.__table__).where( # type: ignore
            MessageBase.__table__.c.timestamp < oldest_timestamp_to_be_kept
        ) 
        conn.execute(stmt)



def _serialized_car_info(company_name:str, car_name:str)->str:
    return f"{company_name}_{car_name}"

def _serialized_device_id(device_id:DeviceId)->str:
    return f"{device_id.module_id}_{device_id.type}_{device_id.role}"



def __all_available_devices(car_info:str)->List[str]:
    device_id_list:List[str] = list()
    for module_devices in device_ids()[car_info].values():
        device_id_list.extend(module_devices)
    return device_id_list

def __available_devices_for_module(car_info:str, module_id:int)->List[str]:
    if not module_id in device_ids()[car_info]: 
        return [], 404 # type: ignore
    else: 
        return device_ids()[car_info][module_id]



@dataclasses.dataclass
class MessageBase(Base):
    __tablename__:ClassVar[str] = "message"
    timestamp:Mapped[int] = mapped_column(primary_key=True)
    sent_order:Mapped[int] = mapped_column(primary_key=True)

    company_name:Mapped[str] = mapped_column(primary_key=True)
    car_name:Mapped[str] = mapped_column(primary_key=True)

    module_id:Mapped[int] = mapped_column(primary_key=True)
    device_type:Mapped[int] = mapped_column(primary_key=True)
    device_role:Mapped[str] = mapped_column(primary_key=True)
    device_name:Mapped[str] = mapped_column()

    payload_type:Mapped[int] = mapped_column(Integer, primary_key=True)
    payload_encoding:Mapped[str] = mapped_column(String)
    payload_data:Mapped[dict] = mapped_column(JSON)
    
    @staticmethod
    def from_model(company_name:str, car_name:str, model:Message, order:int=0)->MessageBase:
        return MessageBase(
            timestamp=model.timestamp,
            sent_order=order,

            company_name=company_name,
            car_name=car_name,

            module_id = model.id.module_id,
            device_type = model.id.type,
            device_role = model.id.role,
            device_name = model.id.name,
            payload_type = model.payload.type, 
            payload_encoding=model.payload.encoding,
            payload_data=model.payload.data # type: ignore
        )

    @staticmethod
    def from_models(company_name:str, car_name:str, *models:Message)->List[MessageBase]:
        bases:List[MessageBase] = list()
        for k in range(len(models)):
            bases.append(MessageBase.from_model(company_name, car_name, models[k], k))
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



# def available_devices(company_name:str, car_name:str, module_id:Optional[int]=None)->List[DeviceId]:  # noqa: E501
#     device_ids:List[DeviceId] = list()
#     with Session(connection_source()) as session:
#         if module_id is not None:
#             result = session.execute(
#                 select(MessageBase).where(
#                     MessageBase.__table__.c.module_id == module_id,
#                     MessageBase.__table__.c.company_name == company_name,
#                     MessageBase.__table__.c.car_name == car_name
#                 )
#             )
#         else:
#             result = session.execute(
#                 select(MessageBase).where(
#                     MessageBase.__table__.c.company_name == company_name,
#                     MessageBase.__table__.c.car_name == car_name
#                 )
#             )
#         for row in result:
#             devicebase:MessageBase = row[0]
#             serialized_id = _serialized_device_id(devicebase.to_model().id)
#             device_ids.append(serialized_id)

#     return device_ids
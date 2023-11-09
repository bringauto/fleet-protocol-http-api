from __future__ import annotations


from typing import ClassVar, List
import connexion
import dataclasses
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import insert, delete, select, JSON


from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.models.device import Device
from fleetv2_http_api.impl.db import connection_source, Base



@dataclasses.dataclass
class DeviceBase(Base):
    __tablename__:ClassVar[str] = "device"
    timestamp:Mapped[int] = mapped_column(primary_key=True)
    id:Mapped[int] = mapped_column(primary_key=True)
    payload_type:Mapped[int]
    payload_encoding:Mapped[str]
    payload_data:Mapped[dict] = mapped_column(JSON)

    @staticmethod
    def from_model(model:Device)->DeviceBase:
        return DeviceBase(
            timestamp=model.timestamp,
            id = model.id,
            payload_type=model.payload.type,
            payload_encoding=model.payload.encoding,
            payload_data=model.payload.data
        )

    def to_model(self)->Device:
        return Device(
            timestamp=self.timestamp,
            id = self.id,
            payload=Payload(self.payload_type, self.payload_encoding, self.payload_data)
        )
    

def add_device(company_name:str, car_name:str, device:Device)->None:
    devicebase = DeviceBase.from_model(device)
    with connection_source().begin() as conn:
        stmt = insert(DeviceBase.__table__)
        conn.execute(stmt, devicebase.__dict__)


def devices_available(company_name:str, car_name:str, module_id:int=None)->List[Device]:  # noqa: E501
    """devices_available

    Returns list of available devices for the whole car or a single module. # noqa: E501

    :param company_name: Name of the company operating/running the car
    :type company_name: str
    :param car_name: Name of the the car
    :type car_name: str
    :param module_id: An Id of module.
    :type module_id: dict | bytes

    :rtype: Union[List[Device], Tuple[List[Device], int], Tuple[List[Device], int, Dict[str, str]]
    """
    # if connexion.request.is_json:
    #     module_id =  object.from_dict(connexion.request.get_json())  # noqa: E501
    devices:List[Device] = list()
    with Session(connection_source()) as session:
        result = session.execute(select(DeviceBase))
        for row in result:
            devicebase:DeviceBase = row[0]
            devices.append(devicebase.to_model())
    return devices


def list_commands(device_id, company_name, car_name, all=None, since=None):  # noqa: E501
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
    return 'do some magic!'


def list_statuses(device_id, company_name, car_name, all=None, since=None):  # noqa: E501
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
    return 'do some magic!'


def send_commands(device_id, company_name, car_name, all=None, since=None, payload=None):  # noqa: E501
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


def send_statuses(device_id, company_name, car_name, all=None, since=None):  # noqa: E501
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

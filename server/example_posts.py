
from server.fleetv2_http_api.impl.controllers import (
    DeviceId,
    Payload,
    send_statuses,
    send_commands,
    Message
)

from enums import MessageType, EncodingType
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial
from server.fleetv2_http_api.impl.controllers import serialized_device_id
from database.time import timestamp


def __send_message_examples(scheduler:BackgroundScheduler)->None:
    device_id = DeviceId(module_id=47, type=2, role="test_device", name="Test Device")
    sdevice_id = serialized_device_id(device_id)
    payload_1 = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"test_status_data": "Connected"})
    payload_2 = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"test_status_data": "Still connected"})
    payload_3 = Payload(type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"test_command_data": "Stay online"})
    
    tstamp_1 = timestamp()
    tstamp_2 = tstamp_1 + 10
    tstamp_3 = tstamp_2 + 10
    status_1 = Message(timestamp=tstamp_1, device_id=device_id, payload=payload_1)
    status_2 = Message(timestamp=tstamp_2, device_id=device_id, payload=payload_2)
    status_3 = Message(timestamp=tstamp_3, device_id=device_id, payload=payload_3)
    
    send_statuses("test_company", "test_car", sdevice_id, [status_1])
    send_statuses("test_company", "test_car", sdevice_id, [status_2])
    send_commands("test_company", "test_car", sdevice_id, [status_3])


def example(scheduler:BackgroundScheduler)->None:
    scheduler.add_job(
        func=partial(__send_message_examples, scheduler=scheduler), 
        id = "posting3" ,
        trigger="interval", 
        seconds=5,
    )

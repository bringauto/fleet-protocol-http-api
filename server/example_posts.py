

from fleetv2_http_api.impl.device_controller import (
    DeviceId,
    Payload,
    send_statuses,
    send_commands,
    Message,
    timestamp
)

from enums import MessageType, EncodingType
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial
from fleetv2_http_api.impl.device_controller import available_cars, _serialized_device_id


def __send_message_examples(scheduler:BackgroundScheduler)->None:
    device_id = DeviceId(module_id=47, type=2, role="test_device", name="Test Device")
    sdevice_id = _serialized_device_id(device_id)
    payload_1 = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"test_status_data": "Connected"})
    payload_2 = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"test_status_data": "Still connected"})
    payload_3 = Payload(type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"test_command_data": "Stay online"})
    
    tstamp_1 = timestamp()
    tstamp_2 = tstamp_1 + 10
    tstamp_3 = tstamp_2 + 10
    status_1 = Message(timestamp=tstamp_1, id=device_id, payload=payload_1)
    status_2 = Message(timestamp=tstamp_2, id=device_id, payload=payload_2)
    status_3 = Message(timestamp=tstamp_3, id=device_id, payload=payload_3)
    
    send_statuses("test_company", "test_car", sdevice_id, [status_1])
    send_statuses("test_company", "test_car", sdevice_id, [status_2])
    send_commands("test_company", "test_car", sdevice_id, [status_3])


# k = 1
# def __post_statuses(scheduler:BackgroundScheduler)->None:
#     global k
#     device_id = DeviceId(module_id=42+2*k, type=4, role="test_device", name="Test Device")
#     sdevice_id = _serialized_device_id(device_id)
#     payload = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={})
#     message = Message(timestamp=timestamp(), id=device_id, payload=payload)
#     send_statuses("company", f"test_car_{k}", sdevice_id, [message])
#     k += 1
#     if k>3: scheduler.remove_job("posting")



def example(scheduler:BackgroundScheduler)->None:
    # scheduler.add_job(
    #     func=partial(__post_statuses, scheduler=scheduler), 
    #     id = "posting" ,
    #     trigger="interval", 
    #     seconds=1,
    # )
    scheduler.add_job(
        func=partial(__send_message_examples, scheduler=scheduler), 
        id = "posting3" ,
        trigger="interval", 
        seconds=5,
    )

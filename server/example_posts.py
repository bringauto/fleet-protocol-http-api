

from fleetv2_http_api.impl.device_controller import DeviceId, Payload, send_statuses
from enums import MessageType, EncodingType
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial
from fleetv2_http_api.impl.device_controller import available_cars


k = 1
def __post_statuses(scheduler:BackgroundScheduler)->None:
    global k
    device_id = DeviceId(module_id=42+2*k, type=4, role="test_device", name="Test Device")
    payload = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={})
    send_statuses("company", f"test_car_{k}", device_id, [payload])
    k += 1
    if k>3: scheduler.remove_job("posting")


def __post_example_status(scheduler:BackgroundScheduler)->None:
    device_id = DeviceId(module_id=47, type=2, role="test_device", name="Test Device")
    payload = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"test_status_data": "Still connected"})
    send_statuses("test_company", "test_car", device_id, [payload])

# def __print_available_cars()->None:
#     print(available_cars())


def example(scheduler:BackgroundScheduler)->None:
    scheduler.add_job(
        func=partial(__post_statuses, scheduler=scheduler), 
        id = "posting" ,
        trigger="interval", 
        seconds=2,
    )
    # scheduler.add_job(
    #     func=__print_available_cars,
    #     id = "posting2" ,
    #     trigger="interval", 
    #     seconds=1,
    # )
    scheduler.add_job(
        func=partial(__post_example_status, scheduler=scheduler), 
        id = "posting3" ,
        trigger="interval", 
        seconds=3,
    )

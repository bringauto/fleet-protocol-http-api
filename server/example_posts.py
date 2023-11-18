

from fleetv2_http_api.impl.device_controller import Payload, send_statuses, send_commands
from enums import MessageType, EncodingType
from apscheduler.schedulers.background import BackgroundScheduler
from functools import partial
from fleetv2_http_api.impl.device_controller import available_cars


k = 1
def __post_statuses(scheduler:BackgroundScheduler)->None:
    global k
    device_id = f"{42+2*k}_4_test_device"
    payload = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={})
    send_statuses("company", f"test_car_{k}", device_id, [payload])
    k += 1
    if k>3: scheduler.remove_job("posting")


from time import sleep
def __post_example_status(scheduler:BackgroundScheduler)->None:
    device_id = "47_2_test_device"
    sleep(1)
    payload_1 = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"test_status_data": "Connected"})
    payload_2 = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={"test_status_data": "Still connected"})
    payload_3 = Payload(type=MessageType.COMMAND_TYPE, encoding=EncodingType.JSON, data={"test_command_data": "Stay online"})
    send_statuses("test_company", "test_car", device_id, [payload_1])
    send_statuses("test_company", "test_car", device_id, [payload_2])
    send_commands("test_company", "test_car", device_id, [payload_3])

# def __print_available_cars()->None:
#     print(available_cars())


def example(scheduler:BackgroundScheduler)->None:
    scheduler.add_job(
        func=partial(__post_statuses, scheduler=scheduler), 
        id = "posting" ,
        trigger="interval", 
        seconds=1,
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
        seconds=5,
    )

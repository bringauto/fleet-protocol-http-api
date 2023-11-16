# Fleet Protocol v2 HTTP API 
# Copyright (C) 2023 BringAuto s.r.o.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import sys
sys.path.append("server")


from fleetv2_http_api.__main__ import main as run_server
from database.database_controller import set_db_connection, remove_old_messages, set_message_retention_period
from database.device_ids import clear_device_ids
from database.time import timestamp


from fleetv2_http_api.impl.device_controller import available_cars

from apscheduler.schedulers.background import BackgroundScheduler


import json
from typing import Any, Dict



def connect_to_database(db_server_config:Dict[str,Any])->None:
    clear_device_ids()
    set_db_connection(
        dialect = db_server_config["dialect"],
        dbapi = db_server_config["api"],
        dblocation = str(db_server_config["host"]) + ":" + str(db_server_config["port"]),
        username = db_server_config["username"],
        password = db_server_config["password"]
    )


scheduler = BackgroundScheduler()


def setup_database_jobs(db_cleanup_config:Dict[str,int])->None:
    global scheduler
    set_message_retention_period(db_cleanup_config["retention_period"])
    scheduler.add_job(
        func=__clean_up_messages, 
        trigger="interval", 
        seconds=db_cleanup_config["cleanup_period"],
    )

    scheduler.add_job(
        func=__post_statuses,
        id = "posting" ,
        trigger="interval", 
        seconds=2,
    )
    scheduler.start()



def __clean_up_messages()->None:
    remove_old_messages(current_timestamp=timestamp())
    print(available_cars())


from fleetv2_http_api.impl.device_controller import DeviceId, Payload, send_statuses
from enums import MessageType, EncodingType


k = 1
def __post_statuses()->None:
    global k, scheduler

    device_id = DeviceId(module_id=42+2*k, type=4, role="test_device", name="Test Device")
    payload = Payload(type=MessageType.STATUS_TYPE, encoding=EncodingType.JSON, data={})
    send_statuses("company", f"test_car_{k}", device_id, [payload])

    k += 1
    
    if k>3: scheduler.remove_job("posting")


if __name__ == '__main__':
    config:Dict[str,Any] = json.load(open("config.json"))
    connect_to_database(config["database"]["server"])
    setup_database_jobs(config["database"]["cleanup"]["timing_in_seconds"])
    __post_statuses()
    run_server()

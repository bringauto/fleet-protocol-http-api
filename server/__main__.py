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
from database.database_controller import set_connection_source, remove_old_messages
from database.device_ids import clear_device_ids
from database.time import timestamp


from fleetv2_http_api.impl.device_controller import available_cars

from apscheduler.schedulers.background import BackgroundScheduler


def connect_to_database()->None:
    clear_device_ids()
    set_connection_source(
        dialect="postgresql",
        dbapi="psycopg",
        dblocation="localhost:5432",
        username="postgres",
        password="1234"
    )


scheduler = BackgroundScheduler()


def schedule_jobs()->None:
    global scheduler
    scheduler.add_job(
        func=__clean_up_messages, 
        trigger="interval", 
        seconds=1,
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
    connect_to_database()
    schedule_jobs()
    __post_statuses()
    run_server()

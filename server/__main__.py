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
from fleetv2_http_api.impl.device_controller import available_cars, list_statuses, DeviceId, send_statuses, Payload
from database.time import timestamp


from apscheduler.schedulers.background import BackgroundScheduler

device_id = DeviceId(module_id=42, type=4, role="test_device", name="Test Device")
payload = Payload(type=0, encoding="JSON", data={"message": "Device is alive"})


def __clean_up_and_list_statuses()->None:
    remove_old_messages(current_timestamp=timestamp())
    # print(list_statuses("test_company", "test_car", device_id, all)[0])
    print(available_cars())
    print()

def __send_statuses()->None:
    send_statuses("test_company", "test_car", device_id, [payload])




def schedule_message_cleanup()->None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=__clean_up_and_list_statuses, 
        trigger="interval", 
        seconds=1
    )
    scheduler.start()

def connect_to_database()->None:
    clear_device_ids()
    set_connection_source(
        dialect="postgresql",
        dbapi="psycopg",
        dblocation="localhost:5432",
        username="postgres",
        password="1234"
    )


if __name__ == '__main__':
    connect_to_database()
    schedule_message_cleanup()
    __send_statuses()
    run_server()


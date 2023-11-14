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
from server.database.database_controller import set_connection_source
from server.database.device_ids import clear_device_ids


def connect_to_database()->None:
    clear_device_ids()
    set_connection_source(
        dialect="postgresql",
        dbapi="psycopg",
        dblocation="localhost:5432",
        username="postgres",
        password="1234"
    )


import time
from apscheduler.schedulers.background import BackgroundScheduler
def __print_current_time()->None:
    print(time.time())


def schedule_message_cleanup()->None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=__print_current_time, trigger="interval", seconds=1)
    scheduler.start()


if __name__ == '__main__':
    connect_to_database()
    # schedule_message_cleanup()
    run_server()

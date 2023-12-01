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


from apscheduler.schedulers.background import BackgroundScheduler
import json
from typing import Any, Dict, List


from database.database_controller import remove_old_messages, set_message_retention_period
from database.device_ids import clear_device_ids
from database.connection import set_db_connection, get_connection_source
from database.time import timestamp
from fleetv2_http_api.__main__ import main as run_server
from database.security import add_admin, number_of_admins


def add_first_clients()->List[str]:
    clients:List[str] = list()
    if number_of_admins() == 0:
        clients.append(add_admin(get_connection_source(), name="admin_01"))
    return clients


def __connect_to_database(db_server_config:Dict[str,Any])->None:
    """Clear previously stored available devices and connect to the database."""
    clear_device_ids()
    set_db_connection(
        dialect = db_server_config["dialect"],
        dbapi = db_server_config["api"],
        dblocation = str(db_server_config["host"]) + ":" + str(db_server_config["port"]),
        username = db_server_config["username"],
        password = db_server_config["password"]
    )


from example_posts import example
def set_up_database_jobs(db_cleanup_config:Dict[str,int])->None:
    """Set message cleanup job and other customary jobs defined by the example method."""
    scheduler = BackgroundScheduler()
    set_message_retention_period(db_cleanup_config["retention_period"])
    scheduler.add_job(
        func=__clean_up_messages, 
        trigger="interval", 
        seconds=db_cleanup_config["cleanup_period"],
    )
    example(scheduler=scheduler)
    scheduler.start()


def __clean_up_messages()->None:
    """Clean up messages from the database."""
    remove_old_messages(current_timestamp=timestamp())


if __name__ == '__main__':
    config:Dict[str,Any] = json.load(open("config.json"))
    __connect_to_database(config["database"]["server"])
    add_first_clients()
    set_up_database_jobs(config["database"]["cleanup"]["timing_in_seconds"])
    run_server()

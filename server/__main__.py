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
from typing import Dict


from database.database_controller import remove_old_messages, set_message_retention_period
from database.device_ids import clear_device_ids
from database.connection import set_db_connection
from database.time import timestamp
from fleetv2_http_api.__main__ import main as run_server
from fleetv2_http_api.impl.controllers import set_status_wait_timeout_s, set_command_wait_timeout_s
import database.script_args as script_args



def __clean_up_messages()->None:
    """Clean up messages from the database."""
    remove_old_messages(current_timestamp=timestamp())


def __connect_to_database(vals:script_args.Script_Args)->None:
    """Clear previously stored available devices and connect to the database."""
    clear_device_ids()
    set_db_connection(
        dblocation = vals.argvals["location"] + ":" + str(vals.argvals["port"]),
        username = vals.argvals["username"],
        password = vals.argvals["password"]
    )


def __set_up_database_jobs(db_cleanup_config:Dict[str,int])->None:
    """Set message cleanup job and other customary jobs defined by the example method."""
    set_message_retention_period(db_cleanup_config["retention_period"])
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=__clean_up_messages, 
        trigger="interval", 
        seconds=db_cleanup_config["cleanup_period"],
    )
    scheduler.start()


if __name__ == '__main__':
    vals = script_args.request_and_get_script_arguments("Run the Fleet Protocol v2 HTTP API server.")
    config = vals.config
    __connect_to_database(vals)
    __set_up_database_jobs(config["database"]["cleanup"]["timing_in_seconds"])
    set_status_wait_timeout_s(config["request_for_messages"]["timeout_in_seconds"])
    set_command_wait_timeout_s(config["request_for_messages"]["timeout_in_seconds"])

    run_server()

import sys
sys.path.append("server")
from unittest.mock import patch, Mock
from fleetv2_http_api.models.device_id import DeviceId
from database.device_ids import serialized_device_id
from database.database_connection import (
    set_db_connection, 
    unset_connection_source, 
    Connection_Source_Not_Set,
    get_connection_source
)

import unittest
from database.database_controller import (
    send_messages_to_database,
    list_messages,
    cleanup_device_commands_and_warn_before_future_commands,
    remove_old_messages,
    Message_DB,
    MessageType,
    MessageBase
)


class TestDatabaseController(unittest.TestCase):

    def setUp(self):
        # Set up the database connection before running the tests
        set_db_connection(dialect="sqlite", dbapi="pysqlite", dblocation="/:memory:")

    def test_accessing_not_set_connection_source_raises_exception(self):
        unset_connection_source()
        self.assertRaises(Connection_Source_Not_Set, get_connection_source)
        
    @patch("database.time._time_in_ms")
    def test_send_messages_to_database(self, mock_time_in_ms:Mock):
        mock_time_in_ms.return_value = 80
        device_id_1 = DeviceId(module_id=45, type=2, role="role1", name="device1")
        sdevice_id_1 = serialized_device_id(device_id_1)
        device_id_2 = DeviceId(module_id=45, type=2, role="role1", name="device2")
        sdevice_id_2 = serialized_device_id(device_id_1)

        message1 = Message_DB(
            timestamp=1,

            serialized_device_id=sdevice_id_1,
            module_id=device_id_1.module_id,
            device_type=device_id_1.type,
            device_role=device_id_1.role,
            device_name=device_id_1.name,

            message_type=2,
            payload_encoding=1,
            payload_data={"key1": "value1"},
        )
        message2 = Message_DB(
            timestamp=7,

            serialized_device_id=sdevice_id_2,
            module_id=device_id_2.module_id,
            device_type=device_id_2.type,
            device_role=device_id_2.role,
            device_name=device_id_2.name,

            message_type=2,
            payload_encoding=2,
            payload_data={"key2": "value2"},
        )
        send_messages_to_database("company1", "car1", message1, message2)

        # Check that the messages were added to the database
        messages = list_messages(
            company_name="company1", 
            car_name="car1",
            message_type=2,
            serialized_device_id=sdevice_id_1,
            all_available=""
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].timestamp, 1)
        self.assertEqual(messages[1].timestamp, 7)

    def test_cleanup_device_commands_and_warn_before_future_commands(self):
        # Test cleaning up device commands and warning before future commands
        device_id = DeviceId(module_id=45, type=2, role="role1", name="device1")
        sdevice_id = serialized_device_id(device_id)
        cleanup_device_commands_and_warn_before_future_commands(
            current_timestamp=100,
            company_name="company1",
            car_name="car1",
            serialized_device_id=sdevice_id
        )

        # Check that the device commands were cleaned up
        messages = list_messages(
            company_name="company1", 
            car_name="car1", 
            message_type=MessageType.COMMAND_TYPE,
            serialized_device_id=sdevice_id,
            all_available=""
        )
        self.assertEqual(len(messages), 0)

    @patch("database.time._time_in_ms")
    def test_remove_old_messages(self, mock_time_in_ms:Mock):
        device_id = DeviceId(module_id=45, type=2, role="role1", name="device1")
        sdevice_id = serialized_device_id(device_id)
        message1 = Message_DB(
            timestamp=0,
            serialized_device_id=sdevice_id,
            
            module_id=device_id.module_id,
            device_type=device_id.type,
            device_role=device_id.role,
            device_name=device_id.name,
            message_type=MessageType.STATUS_TYPE,
            payload_encoding=1,
            payload_data={"key1": "value1"},
        )
        message2 = Message_DB(
            timestamp=50,

            serialized_device_id=sdevice_id,
            module_id=device_id.module_id,
            device_type=device_id.type,
            device_role=device_id.role,
            device_name=device_id.name,
            message_type=MessageType.STATUS_TYPE,
            payload_encoding=2,
            payload_data={"key2": "value2"},
        )
        send_messages_to_database("company1", "car1", message1, message2)

        mock_time_in_ms.return_value = MessageBase.data_retention_period_ms + 1 
        # Remove old messages from the database
        remove_old_messages(mock_time_in_ms.return_value)

        # Check that the old messages were removed from the database
        messages = list_messages(
            company_name="company1", 
            car_name="car1", 
            message_type=MessageType.STATUS_TYPE,
            serialized_device_id=sdevice_id,
            all_available=""
        )
        self.assertEqual(len(messages), 1)



if __name__ == "__main__":
    unittest.main()

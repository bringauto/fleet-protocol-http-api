import sys
sys.path.append("server")
from unittest.mock import patch, Mock


import unittest
from database.database_controller import (
    set_db_connection,
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
        

    @patch("database.time._time_in_ms")
    def test_send_messages_to_database(self, mock_time_in_ms:Mock):
        mock_time_in_ms.return_value = 80

        message1 = Message_DB(
            timestamp=1,

            module_id=45,
            device_type=2,
            device_role="role1",

            device_name="device1",
            message_type=2,
            payload_encoding=1,
            payload_data={"key1": "value1"},
        )
        message2 = Message_DB(
            timestamp=7,

            module_id=45,
            device_type=2,
            device_role="role1",

            device_name="device2",
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

            module_id=45,
            device_type=2,
            device_role="role1",

            all=True
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].timestamp, 1)
        self.assertEqual(messages[1].timestamp, 7)

    def test_cleanup_device_commands_and_warn_before_future_commands(self):
        # Test cleaning up device commands and warning before future commands
        cleanup_device_commands_and_warn_before_future_commands(
            current_timestamp=100,
            company_name="company1",
            car_name="car1",
            module_id=1,
            device_type=1,
            device_role="role1",
        )

        # Check that the device commands were cleaned up
        messages = list_messages(
            company_name="company1", 
            car_name="car1", 
            message_type=MessageType.COMMAND_TYPE,
            module_id=45,
            device_type=1,
            device_role="role1",
            all=True
        )
        self.assertEqual(len(messages), 0)

    @patch("database.time._time_in_ms")
    def test_remove_old_messages(self, mock_time_in_ms:Mock):

        message1 = Message_DB(
            timestamp=0,

            module_id=43,
            device_type=2,
            device_role="role2",

            device_name="device2",
            message_type=MessageType.STATUS_TYPE,
            payload_encoding=1,
            payload_data={"key1": "value1"},
        )
        message2 = Message_DB(
            timestamp=50,

            device_type=2,
            module_id=43,
            device_role="role2",

            device_name="device2",
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

            module_id=43,
            device_type=2,
            device_role="role2",

            all=True
        )
        self.assertEqual(len(messages), 1)



if __name__ == "__main__":
    unittest.main()

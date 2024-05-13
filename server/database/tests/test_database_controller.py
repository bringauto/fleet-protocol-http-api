import os
import sys

sys.path.append("server")

from unittest.mock import patch, Mock
import unittest
from enums import EncodingType, MessageType  # type: ignore

from fleetv2_http_api.models.device_id import DeviceId  # type: ignore
from database.connected_cars import serialized_device_id  # type: ignore
from database.connection import (  # type: ignore
    set_test_db_connection,
    unset_connection_source,
    ConnectionSourceNotSet,
    get_connection_source,
    set_test_db_connection,
)
from database.database_controller import (  # type: ignore
    set_message_retention_period,
    send_messages_to_database,
    list_messages,
    cleanup_device_commands_and_warn_before_future_commands,
    remove_old_messages,
    Message_DB,
    MessageBase,
)
from fleetv2_http_api.impl.controllers import DeviceId  # type: ignore


class Test_Creating_And_Reading_MessageBase_Objects(unittest.TestCase):
    def test_creating_message_base_object_from_message(self):
        company_name = "test_company"
        car_name = "test_car"
        device_id = DeviceId(module_id=45, type=2, role="role1", name="device1")
        sdevice_id = serialized_device_id(device_id)
        message_db = Message_DB(
            timestamp=100,
            serialized_device_id=sdevice_id,
            module_id=device_id.module_id,
            device_type=device_id.type,
            device_role=device_id.role,
            device_name=device_id.name,
            message_type=MessageType.STATUS,
            payload_encoding=EncodingType.JSON,
            payload_data={"content": "..."},
        )
        message_base = MessageBase.from_message(company_name, car_name, message_db)
        self.assertEqual(message_base.company_name, company_name)
        self.assertEqual(message_base.car_name, car_name)
        self.assertEqual(message_base.timestamp, 100)
        self.assertEqual(message_base.module_id, device_id.module_id)
        self.assertEqual(message_base.device_type, device_id.type)
        self.assertEqual(message_base.device_role, device_id.role)
        self.assertEqual(message_base.device_name, device_id.name)
        self.assertEqual(message_base.message_type, MessageType.STATUS)
        self.assertEqual(message_base.payload_encoding, EncodingType.JSON)
        self.assertEqual(message_base.payload_data, {"content": "..."})

    def test_creating_message_from_base_object(self):
        base = MessageBase(
            company_name="test_company",
            car_name="test_car",
            timestamp=100,
            module_id=45,
            device_type=2,
            device_role="role1",
            device_name="device1",
            message_type=MessageType.STATUS,
            payload_encoding=EncodingType.JSON,
            payload_data={"content": "..."},
        )
        message_db = MessageBase.to_message(base)
        self.assertEqual(message_db.timestamp, 100)
        self.assertEqual(message_db.module_id, 45)
        self.assertEqual(message_db.device_type, 2)
        self.assertEqual(message_db.device_role, "role1")
        self.assertEqual(message_db.device_name, "device1")
        self.assertEqual(message_db.message_type, MessageType.STATUS)
        self.assertEqual(message_db.payload_encoding, EncodingType.JSON)
        self.assertEqual(message_db.payload_data, {"content": "..."})


class Test_Specifying_Database_Name(unittest.TestCase):
    def test_setting_database_name(self):
        set_test_db_connection(db_name="test_db.db")
        source = get_connection_source()
        self.assertEqual(source.url.database, "test_db.db")
        if os.path.isfile("test_db.db"):
            os.remove("test_db.db")


class Test_Sending_And_Clearing_Messages(unittest.TestCase):
    def setUp(self):
        # Set up the database connection before running the tests
        set_test_db_connection()

    def test_accessing_not_set_connection_source_raises_exception(self):
        unset_connection_source()
        self.assertRaises(ConnectionSourceNotSet, get_connection_source)

    @patch("database.time._time_in_ms")
    def test_send_messages_to_database(self, mock_time_in_ms: Mock):
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
            message_type=MessageType.STATUS,
            payload_encoding=EncodingType.BASE64,
            payload_data={"key1": "value1"},
        )
        message2 = Message_DB(
            timestamp=7,
            serialized_device_id=sdevice_id_2,
            module_id=device_id_2.module_id,
            device_type=device_id_2.type,
            device_role=device_id_2.role,
            device_name=device_id_2.name,
            message_type=MessageType.STATUS,
            payload_encoding=EncodingType.BASE64,
            payload_data={"key2": "value2"},
        )
        mock_time_in_ms.return_value = 1
        send_messages_to_database("company1", "car1", message1)
        mock_time_in_ms.return_value = 7
        send_messages_to_database("company1", "car1", message2)

        # Check that the messages were added to the database
        messages = list_messages(
            company_name="company1",
            car_name="car1",
            message_type=MessageType.STATUS,
        )
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].timestamp, 1)
        self.assertEqual(messages[1].timestamp, 7)

    @patch("database.time._time_in_ms")
    def test_cleanup_device_commands_and_warn_before_future_commands(self, mock_time_in_ms: Mock):
        device_id = DeviceId(module_id=45, type=2, role="role1", name="device1")
        sdevice_id = serialized_device_id(device_id)

        mock_time_in_ms.return_value = 0
        send_messages_to_database(
            "test_company",
            "test_car",
            Message_DB(
                timestamp=0,
                serialized_device_id=sdevice_id,
                module_id=device_id.module_id,
                device_type=device_id.type,
                device_role=device_id.role,
                device_name=device_id.name,
                message_type=MessageType.STATUS,
                payload_encoding=EncodingType.JSON,
                payload_data={"key1": "value1"},
            ),
        )
        mock_time_in_ms.return_value = MessageBase.data_retention_period_ms() + 100
        send_messages_to_database(
            "test_company",
            "test_car",
            Message_DB(
                timestamp=MessageBase.data_retention_period_ms() + 100,
                serialized_device_id=sdevice_id,
                module_id=device_id.module_id,
                device_type=device_id.type,
                device_role=device_id.role,
                device_name=device_id.name,
                message_type=MessageType.COMMAND,
                payload_encoding=EncodingType.JSON,
                payload_data={"key1": "value1"},
            ),
        )
        mock_time_in_ms.return_value = MessageBase.data_retention_period_ms() + 150
        send_messages_to_database(
            "test_company",
            "test_car",
            Message_DB(
                timestamp=MessageBase.data_retention_period_ms() + 150,
                serialized_device_id=sdevice_id,
                module_id=device_id.module_id,
                device_type=device_id.type,
                device_role=device_id.role,
                device_name=device_id.name,
                message_type=MessageType.COMMAND,
                payload_encoding=EncodingType.JSON,
                payload_data={"key1": "value1"},
            ),
        )
        remove_old_messages(current_timestamp=MessageBase.data_retention_period_ms() + 50)
        self.assertEqual(len(list_messages("test_company", "test_car", MessageType.STATUS)), 0)
        warnings = cleanup_device_commands_and_warn_before_future_commands(
            current_timestamp=MessageBase.data_retention_period_ms() + 55,
            company_name="test_company",
            car_name="test_car",
            serialized_device_id=sdevice_id,
        )

        self.assertEqual(len(warnings), 2)
        # Check that the device commands were cleaned up
        messages = list_messages(
            company_name="test_company",
            car_name="test_car",
            message_type=MessageType.COMMAND,
        )
        self.assertEqual(len(messages), 0)

    @patch("database.time._time_in_ms")
    def test_remove_old_messages(self, mock_time_in_ms: Mock):
        device_id = DeviceId(module_id=45, type=2, role="role1", name="device1")
        sdevice_id = serialized_device_id(device_id)
        message1 = Message_DB(
            timestamp=0,
            serialized_device_id=sdevice_id,
            module_id=device_id.module_id,
            device_type=device_id.type,
            device_role=device_id.role,
            device_name=device_id.name,
            message_type=MessageType.STATUS,
            payload_encoding=EncodingType.JSON,
            payload_data={"key1": "value1"},
        )
        message2 = Message_DB(
            timestamp=50,
            serialized_device_id=sdevice_id,
            module_id=device_id.module_id,
            device_type=device_id.type,
            device_role=device_id.role,
            device_name=device_id.name,
            message_type=MessageType.STATUS,
            payload_encoding=EncodingType.BASE64,
            payload_data={"key2": "value2"},
        )
        mock_time_in_ms.return_value = 0
        send_messages_to_database("company1", "car1", message1)
        mock_time_in_ms.return_value = 50
        send_messages_to_database("company1", "car1", message2)

        mock_time_in_ms.return_value = MessageBase.data_retention_period_ms() + 1
        # Remove old messages from the database
        remove_old_messages(mock_time_in_ms.return_value)

        # Check that the old messages were removed from the database
        messages = list_messages(
            company_name="company1",
            car_name="car1",
            message_type=MessageType.STATUS,
        )
        self.assertEqual(len(messages), 1)


class Test_Database_Cleanup(unittest.TestCase):
    def setUp(self):
        # Set up the database connection before running the tests
        set_test_db_connection(dblocation="/:memory:")

    def test_setting_and_accessing_data_retention_period(self):
        MessageBase.set_data_retention_period(seconds=3)
        self.assertEqual(MessageBase.data_retention_period_ms(), 3000)
        set_message_retention_period(seconds=5)
        self.assertEqual(MessageBase.data_retention_period_ms(), 5000)

    def test_setting_other_than_positive_integer_retention_period_is_ignored(self):
        set_message_retention_period(1)
        self.assertEqual(MessageBase.data_retention_period_ms(), 1000)
        set_message_retention_period(0)
        self.assertEqual(MessageBase.data_retention_period_ms(), 1000)
        set_message_retention_period(-9)
        self.assertEqual(MessageBase.data_retention_period_ms(), 1000)
        set_message_retention_period("abc")  # type: ignore
        self.assertEqual(MessageBase.data_retention_period_ms(), 1000)


class Test_Send_And_Read_Message(unittest.TestCase):
    def setUp(self):
        # Set up the database connection before running the tests
        set_test_db_connection(dblocation="/:memory:")

    @patch("database.time._time_in_ms")
    def test_send_and_read_message(self, mock_time_in_ms: Mock):
        device_id = DeviceId(module_id=45, type=2, role="role1", name="device1")
        sdevice_id = serialized_device_id(device_id)

        message_1 = Message_DB(
            timestamp=100,
            serialized_device_id=sdevice_id,
            module_id=device_id.module_id,
            device_type=device_id.type,
            device_role=device_id.role,
            device_name=device_id.name,
            message_type=MessageType.STATUS,
            payload_encoding=EncodingType.BASE64,
            payload_data={"content": "..."},
        )
        message_2 = Message_DB(
            timestamp=150,
            serialized_device_id=sdevice_id,
            module_id=device_id.module_id,
            device_type=device_id.type,
            device_role=device_id.role,
            device_name=device_id.name,
            message_type=MessageType.STATUS,
            payload_encoding=EncodingType.BASE64,
            payload_data={"content": "other content"},
        )

        mock_time_in_ms.return_value = 100
        send_messages_to_database("test_company", "test_car", message_1)
        mock_time_in_ms.return_value = 150
        send_messages_to_database("test_company", "test_car", message_2)
        # read all statuses
        read_messages = list_messages("test_company", "test_car", MessageType.STATUS)
        self.assertEqual(len(read_messages), 2)
        # read only the last status
        read_messages = list_messages(
            "test_company", "test_car", MessageType.STATUS, since=150
        )
        self.assertEqual(len(read_messages), 1)
        # read only statuses after timestamp 120
        read_messages = list_messages(
            "test_company", "test_car", MessageType.STATUS, since=120
        )
        self.assertEqual(len(read_messages), 1)
        self.assertEqual(read_messages[0].timestamp, 150)


if __name__ == "__main__":
    unittest.main()

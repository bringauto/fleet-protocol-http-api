import sys
sys.path.append("server")


import unittest
from database.device_ids import clear_device_ids, serialized_device_id
from database.database_controller import set_db_connection
from fleetv2_http_api.impl.controllers import (
    send_statuses, 
    list_statuses, 
)
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api.models.message import Payload, Message



import fleetv2_http_api.impl.wait as wait


class Test_Listing_Statuses(unittest.TestCase):

    def setUp(self) -> None:
        set_db_connection("sqlite","pysqlite","/example.db")
        clear_device_ids()
        payload_example = Payload(
            message_type='STATUS', 
            encoding='JSON', 
            data={"message":"Device is running"}
        )
        self.device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Left light")
        self.sdevice_id = serialized_device_id(self.device_id)
        self.status_example = Message(
            timestamp=123456789,
            device_id=self.device_id,
            payload=payload_example
        )

    def test_return_statuses_immediatelly_if_some_are_avaialable(self):
        send_statuses(
            company_name="test_company", 
            car_name="test_car", 
            sdevice_id=self.sdevice_id, 
            messages=[self.status_example]
        )
        statuses, code = list_statuses(company_name="test_company", car_name="test_car", sdevice_id=self.sdevice_id, wait="")
        self.assertEqual(len(statuses), 1)

    def tearDown(self) -> None:
        if os.path.exists("./example.db"):
            os.remove("./example.db")


class Test_Creating_Wait_Objects(unittest.TestCase):

    def setUp(self) -> None:
        self.wd = wait.Wait_Dict()

    def test_adding_new_wait_obj(self):
        self.wd.add("test_company", "test_car", "id_xyz")
        self.assertTrue(self.wd.wait_obj_exists("test_company", "test_car", "id_xyz"))
        self.assertFalse(self.wd.wait_obj_exists("test_company", "other_car", "id_ABC"))

        self.wd.add("test_company", "other_car", "id_ABC")
        self.assertTrue(self.wd.wait_obj_exists("test_company", "other_car", "id_ABC"))

    def test_removing_waiting_object(self)->None:
        self.wd.add("test_company", "test_car", "id_xyz")
        self.assertTrue(self.wd.wait_obj_exists("test_company", "test_car", "id_xyz"))
        self.wd.remove("test_company", "test_car", "id_xyz")
        self.assertFalse(self.wd.wait_obj_exists("test_company", "test_car", "id_xyz"))


class Test_Wait_Manager(unittest.TestCase):

    def setUp(self) -> None:
        self.mg = wait.Wait_Manager()

    def test_wait_for(self)->None:
        self.mg.add_wait_obj("test_company", "test_car", "id_xyz", 78)
        self.mg.is_waiting_for("test_company", "test_car", "id_xyz")

    def test_object_is_removed_after_manually_stopping_waiting_for_it(self):
        self.mg.add_wait_obj("test_company", "test_car", "id_xyz", 78)
        self.mg.stop_waiting_for("test_company", "test_car", "id_xyz")
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_xyz"))

    def test_timeout_of_a_single_obj(self):
        self.mg.add_wait_obj("test_company", "test_car", "id_xyz", 78)
        self.mg.set_timeout(100)
        self.mg.check_timeouts(curr_time_ms=177)
        self.assertTrue(self.mg.is_waiting_for("test_company", "test_car", "id_xyz"))
        self.mg.check_timeouts(curr_time_ms=178)
        self.assertTrue(self.mg.is_waiting_for("test_company", "test_car", "id_xyz"))
        self.mg.check_timeouts(curr_time_ms=179)
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_xyz"))

    def test_when_checking_timeout_objects_with_timestamp_older_than_current_minus_timeout_are_removed(self):
        self.mg.add_wait_obj("test_company", "test_car", "id_1", 40)
        self.mg.add_wait_obj("test_company", "test_car", "id_2", 45)
        self.mg.add_wait_obj("test_company", "test_car", "id_3", 50)
        self.mg.add_wait_obj("test_company", "test_car", "id_4", 55)

        self.mg.set_timeout(10)
        self.mg.check_timeouts(curr_time_ms=60)
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_1"))
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_2"))
        self.assertTrue(self.mg.is_waiting_for("test_company", "test_car", "id_3"))
        self.assertTrue(self.mg.is_waiting_for("test_company", "test_car", "id_4"))
        self.assertTrue(self.mg.waiting_for_anything)

    def test_timeout_of_all_objects(self):
        self.mg.add_wait_obj("test_company", "test_car", "id_1", 40)
        self.mg.add_wait_obj("test_company", "test_car", "id_2", 45)
        self.mg.add_wait_obj("test_company", "test_car", "id_3", 50)
        self.mg.set_timeout(10)
        self.mg.check_timeouts(curr_time_ms=100000000)
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_1"))
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_2"))
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_3"))
        self.assertFalse(self.mg.waiting_for_anything)



import threading
import os 
import time
from fleetv2_http_api.impl.controllers import set_status_wait_timeout_s, get_status_wait_timeout_s

class Test_Ask_For_Statuses_Not_Available_At_The_Time_Of_The_Request(unittest.TestCase):

    def setUp(self) -> None:
        set_db_connection("sqlite","pysqlite","/example.db")
        clear_device_ids()
        payload_example = Payload(
            message_type='STATUS', 
            encoding='JSON', 
            data={"message":"Device is running"}
        )
        self.device_id = DeviceId(module_id=42, type=7, role="test_device_1", name="Left light")
        self.sdevice_id = serialized_device_id(self.device_id)
        self.st = Message(
            timestamp=123456789,
            device_id=self.device_id,
            payload=payload_example
        )
        self.original_timeout = get_status_wait_timeout_s()


    def test_return_statuses_sent_after_the_request_when_wait_mechanism_is_applied(self):

        def list_test_statuses():
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id, wait="")
            self.assertEqual(code, 200)

        def send_single_status():
            time.sleep(0.01) 
            send_statuses("test_company", "test_car", self.sdevice_id, messages=[self.st])

        t_list = threading.Thread(target=list_test_statuses)
        t_send = threading.Thread(target=send_single_status)
        t_list.start()
        t_send.start()
        t_list.join()
        t_send.join()


    def test_return_statuses_sent_after_the_request_without_applying_wait_mechanism(self):

        def list_test_statuses():
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id)
            self.assertEqual(code, 404) # 404 is returned as the list_statuses does not wait for the statuses to arrive

        def send_single_status():
            time.sleep(0.01) 
            send_statuses("test_company", "test_car", self.sdevice_id, messages=[self.st])

        t_list = threading.Thread(target=list_test_statuses)
        t_send = threading.Thread(target=send_single_status)
        t_list.start()
        t_send.start()
        t_list.join()
        t_send.join()

    def test_return_statuses_sent_after_the_request_with_wait_mechanism_with_timeout_exceeded(self):

        def list_test_statuses():
            set_status_wait_timeout_s(0.01)
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id, wait="")
            self.assertEqual(code, 404) # 404 is returned as the list_statuses does not wait for the statuses to arrive

        def send_single_status():
            time.sleep(0.02) 
            send_statuses("test_company", "test_car", self.sdevice_id, messages=[self.st])

        t_list = threading.Thread(target=list_test_statuses)
        t_send = threading.Thread(target=send_single_status)
        t_list.start()
        t_send.start()
        t_list.join()

    def test_sending_empty_statuses_list_does_not_stop_the_waiting(self):

        def list_test_statuses():
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id, wait="")
            self.assertEqual(code, 200) # 404 is returned as the list_statuses does not wait for the statuses to arrive
            self.assertEqual(len(msg), 1)

        def send_single_status():
            time.sleep(0.05) 
            send_statuses("test_company", "test_car", self.sdevice_id, messages=[self.st])

        def send_no_status():
            time.sleep(0.02) 
            send_statuses("test_company", "test_car", self.sdevice_id, messages=[])

        t_list = threading.Thread(target=list_test_statuses)
        t_send_1 = threading.Thread(target=send_no_status)
        t_send_2 = threading.Thread(target=send_single_status)
        t_list.start()
        t_send_1.start()
        t_send_2.start()
        t_list.join()
        t_send_1.join()
        t_send_2.join()


    def tearDown(self) -> None:
        set_status_wait_timeout_s(self.original_timeout)
        if os.path.exists("./example.db"):
            os.remove("./example.db")


if __name__=="__main__": 
    # runner = unittest.TextTestRunner()
    # runner.run(Test_Ask_For_Statuses_Not_Available_At_The_Time_Of_The_Request(
    #     "test_return_statuses_sent_after_the_request_without_applying_wait_mechanism"
    # ))
    # runner.run(Test_Ask_For_Statuses_Not_Available_At_The_Time_Of_The_Request(
    #     "test_return_statuses_sent_after_the_request_when_wait_mechanism_is_applied"
    # ))
    # runner.run(Test_Ask_For_Statuses_Not_Available_At_The_Time_Of_The_Request(
    #     "test_return_statuses_sent_after_the_request_with_wait_mechanism_with_timeout_exceeded"
    # ))
    # runner.run(Test_Ask_For_Statuses_Not_Available_At_The_Time_Of_The_Request(
    #     "test_sending_empty_statuses_list_does_not_stop_the_waiting"
    # ))
    unittest.main()

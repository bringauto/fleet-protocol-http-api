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


class Test_Creating_Wait_Objects(unittest.TestCase):

    def setUp(self) -> None:
        self.wd = wait.Wait_Queue_Dict()

    def test_adding_new_obj(self):
        self.wd.add("test_company", "test_car", "id_xyz")
        self.assertTrue(self.wd.obj_exists("test_company", "test_car", "id_xyz"))
        self.assertFalse(self.wd.obj_exists("test_company", "other_car", "id_ABC"))

        self.wd.add("test_company", "other_car", "id_ABC")
        self.assertTrue(self.wd.obj_exists("test_company", "other_car", "id_ABC"))

    def test_removing_object(self)->None:
        self.wd.add("test_company", "test_car", "id_xyz")
        self.assertTrue(self.wd.obj_exists("test_company", "test_car", "id_xyz"))
        self.wd.remove("test_company", "test_car", "id_xyz")
        self.assertFalse(self.wd.obj_exists("test_company", "test_car", "id_xyz"))

    def test_after_adding_two_wait_objects_and_removing_one_the_obj_exists_method_still_returns_true(self)->None:
        self.wd.add("test_company", "test_car", "id_xyz", obj = "obj_1")
        self.wd.add("test_company", "test_car", "id_xyz", obj = "obj_2")
        self.assertEqual(self.wd.next_in_queue("test_company", "test_car", "id_xyz"), "obj_1")

        self.wd.remove("test_company", "test_car", "id_xyz")
        self.assertTrue(self.wd.obj_exists("test_company", "test_car", "id_xyz"))
        self.assertEqual(self.wd.next_in_queue("test_company", "test_car", "id_xyz"), "obj_2")

        self.wd.remove("test_company", "test_car", "id_xyz")
        self.assertFalse(self.wd.obj_exists("test_company", "test_car", "id_xyz"))
        self.assertEqual(self.wd.next_in_queue("test_company", "test_car", "id_xyz"), None)


class Test_Wait_Manager(unittest.TestCase):

    def setUp(self) -> None:
        self.mg = wait.Wait_Obj_Manager()

    def test_adding_a_wait_object(self)->None:
        wait_obj = self.mg.new_wait_obj("test_company", "test_car", "id_xyz")
        self.mg.is_waiting_for("test_company", "test_car", "id_xyz")
        self.assertEqual(self.mg.next_in_queue("test_company", "test_car", "id_xyz"), wait_obj)

    def test_object_is_removed_after_stopping_waiting_for_it(self):
        self.mg.new_wait_obj("test_company", "test_car", "id_xyz")
        self.mg.stop_waiting_for("test_company", "test_car", "id_xyz")
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_xyz"))
        self.assertEqual(self.mg.next_in_queue("test_company", "test_car", "id_xyz"), None)

    def test_stop_waiting_for_one_of_three_objects_at_a_time(self):
        obj_1 = self.mg.new_wait_obj("test_company", "test_car", "id_xyz")
        obj_2 = self.mg.new_wait_obj("test_company", "test_car", "id_xyz")
        obj_3 = self.mg.new_wait_obj("test_company", "test_car", "id_xyz")
        self.assertEqual(self.mg.next_in_queue("test_company", "test_car", "id_xyz"), obj_1)

        self.mg.stop_waiting_for("test_company", "test_car", "id_xyz")
        self.assertTrue(self.mg.is_waiting_for("test_company", "test_car", "id_xyz"))
        self.assertEqual(self.mg.next_in_queue("test_company", "test_car", "id_xyz"), obj_2)

        self.mg.stop_waiting_for("test_company", "test_car", "id_xyz")
        self.assertTrue(self.mg.is_waiting_for("test_company", "test_car", "id_xyz"))
        self.assertEqual(self.mg.next_in_queue("test_company", "test_car", "id_xyz"), obj_3)

        self.mg.stop_waiting_for("test_company", "test_car", "id_xyz")
        self.assertFalse(self.mg.is_waiting_for("test_company", "test_car", "id_xyz"))
        self.assertEqual(self.mg.next_in_queue("test_company", "test_car", "id_xyz"), None)

    def test_remove_given_wait_object(self):
        obj = self.mg.new_wait_obj("test_company", "test_car", "id_xyz")
        self.assertEqual(self.mg.next_in_queue("test_company", "test_car", "id_xyz"), obj)
        self.mg.remove_wait_obj(obj)
        self.assertEqual(self.mg.next_in_queue("test_company", "test_car", "id_xyz"), None)


import threading
import os 
import time
from fleetv2_http_api.impl.controllers import set_status_wait_timeout_s, get_status_wait_timeout_s

class Test_Ask_For_Statuses_Not_Available_At_The_Time_Of_The_Request(unittest.TestCase):

    def setUp(self) -> None:
        if os.path.exists("./example.db"): os.remove("./example.db")
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
        set_status_wait_timeout_s(1)
        self.original_timeout = get_status_wait_timeout_s()


    def test_return_statuses_sent_after_the_request_when_wait_mechanism_is_applied(self):

        def list_test_statuses():
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id, wait="")
            self.assertEqual(code, 200)
            self.assertEqual(len(msg), 1)

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
            self.assertEqual(len(msg), 0)

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
            self.assertEqual(code, 408)

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
            self.assertEqual(code, 200) 
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

    def test_sending_second_request_does_not_affect_response_for_the_first_one(self):

        set_status_wait_timeout_s(0.02)

        def list_test_statuses_1():
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id, wait="")
            self.assertEqual(code, 408) 

        def list_test_statuses_2():
            time.sleep(0.06)
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id, wait="")
            self.assertEqual(code, 200) 

        def send_single_status():
            time.sleep(0.04)
            send_statuses("test_company", "test_car", self.sdevice_id, messages=[self.st])

        t_list_1 = threading.Thread(target=list_test_statuses_1)
        t_list_2 = threading.Thread(target=list_test_statuses_2)
        t_send = threading.Thread(target=send_single_status)
        t_list_1.start()
        t_list_2.start()
        t_send.start()
        t_list_1.join()
        t_list_2.join()
        t_send.join()

    def test_sending_second_request_after_statuses_are_available_but_before_timeout_succeeds(self):
        TIMEOUT =           0.05
        T_FIRST_REQUEST =   0.00
        T_SECOND_REQUEST =  0.08
        T_STATUSES_SENT =   0.1

        set_status_wait_timeout_s(TIMEOUT)

        def list_test_statuses_1():
            time.sleep(T_FIRST_REQUEST)
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id, wait="")
            self.assertEqual(code, 408) 

        def list_test_statuses_2():
            time.sleep(T_SECOND_REQUEST)
            msg, code = list_statuses("test_company", "test_car", self.sdevice_id, wait="")
            self.assertEqual(code, 200) 

        def send_single_status():
            time.sleep(T_STATUSES_SENT)
            send_statuses("test_company", "test_car", self.sdevice_id, messages=[self.st])

        t_list_1 = threading.Thread(target=list_test_statuses_1)
        t_list_2 = threading.Thread(target=list_test_statuses_2)
        t_send = threading.Thread(target=send_single_status)
        t_list_1.start()
        t_list_2.start()
        t_send.start()
        t_list_1.join()
        t_list_2.join()
        t_send.join()


    def tearDown(self) -> None:
        set_status_wait_timeout_s(self.original_timeout)
        if os.path.exists("./example.db"): os.remove("./example.db")


if __name__=="__main__": 
    unittest.main()

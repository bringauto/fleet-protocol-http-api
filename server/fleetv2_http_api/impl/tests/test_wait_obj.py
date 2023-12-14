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



if __name__=="__main__": 
    unittest.main()
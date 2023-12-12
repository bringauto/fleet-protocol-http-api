from typing import Dict


class Wait_Manager:

    def __init__(self)->None:
        self.__wait_objs:Dict[str, Dict[str, Dict[str, Wait_Manager.Wait_Obj]]] = dict()

    def is_waiting(self, company_name:str, car_name:str, sdevice_id:str)->bool:
        return (
            company_name in self.__wait_objs and
            car_name in self.__wait_objs[company_name] and
            sdevice_id in self.__wait_objs[company_name][car_name]
        )
    
    def stop_waiting(self, company_name:str, car_name:str, sdevice_id:str)->None:
        self.__wait_objs[company_name][car_name].pop(sdevice_id)
        if not self.__wait_objs[company_name][car_name]: self.__wait_objs[company_name].pop(car_name)
        if not self.__wait_objs[company_name]: self.__wait_objs.pop(company_name)
        
    def wait_for(self, company_name:str, car_name:str, sdevice_id:str)->None:
        if company_name not in self.__wait_objs:
            self.__wait_objs[company_name] = {}
        if car_name not in self.__wait_objs[company_name]:
            self.__wait_objs[company_name][car_name] = {}
        if sdevice_id not in self.__wait_objs[company_name][car_name]:
            self.__wait_objs[company_name][car_name][sdevice_id] = self.Wait_Obj()


    class Wait_Obj:
        pass
import sys 
sys.path.append(".")


from http_api_client.api_client import ApiClient
from http_api_client.api.car_api import CarApi 
from http_api_client.api.database_api import DatabaseApi, ConnectToDatabaseRequest


class Client(ApiClient):

    def __init__(self, connect_to:str)->None:
        super().__init__()
        self.configuration.host = connect_to
        self.__db_api = DatabaseApi(self)
        self.api = CarApi(self)


    def connect_to_database(
            self, 
            dialect:str, 
            dbapi:str, 
            location:str, 
            username:str="", 
            password:str=""
        )->None:

        request = ConnectToDatabaseRequest(
            dialect=dialect,
            dbapi=dbapi,
            location=location,
            username=username,
            password=password
        )

        assert(request is not None)
        self.__db_api.connect_to_database(connect_to_database_request=request)
        


    def register_new_car(self, car_name:str, company_name:str)->None:
        pass

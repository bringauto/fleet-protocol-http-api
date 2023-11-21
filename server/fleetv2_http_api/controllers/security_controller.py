from typing import Dict, Literal
import dataclasses


RoleType = Literal["visitor", "maintainer"]


import datetime


@dataclasses.dataclass
class Role:
    role: RoleType
    name: str
    key: str
    check_period_in_seconds:int = 5
    max_requests_per_period:int = 5
    counter:int = dataclasses.field(init=False, default=0)
    last_time:datetime.datetime = dataclasses.field(init=False, default=datetime.datetime.now())

    def get_key(self)->str|None:
        self.__reset_counter_if_period_passed()
        self.counter += 1
        if self.counter>self.max_requests_per_period:
            return None
        else:
            return self.key
        
    def __reset_counter_if_period_passed(self)->None:
        curr_time = datetime.datetime.now()
        if curr_time - self.last_time >= datetime.timedelta(seconds=self.check_period_in_seconds):
            self.last_time = curr_time
            self.counter = 0

    class TooManyRequests(Exception): pass


KEYS:Dict[RoleType, Role] = {
    "visitor": Role(role="visitor", name="visitor", key="visit"),
    "maintainer": Role(role="maintainer", name="maintainer", key="maint"),
}


def info_from_VisitorAuth(api_key, *args)->Dict:
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """
    
    key = KEYS["visitor"].get_key()
    if key == None: 
        return None # type: ignore
    if api_key == key: 
        return {'client role': "visitor"}
    else: 
        return info_from_MaintainerAuth(api_key, *args)

def info_from_MaintainerAuth(api_key, *args)->Dict:
    """
    Check and retrieve authentication information from api_key.
    Returned value will be passed in 'token_info' parameter of your operation function, if there is one.
    'sub' or 'uid' will be set in 'user' parameter of your operation function, if there is one.

    :param api_key API key provided by Authorization header
    :type api_key: str
    :return: Information attached to provided api_key or None if api_key is invalid or does not allow access to called API
    :rtype: dict | None
    """

    key = KEYS["maintainer"].get_key()
    if key == None: 
        return None # type: ignore
    elif api_key == KEYS["maintainer"].get_key(): 
        return {'client role': "maintainer"}
    else: 
        return None # type: ignore

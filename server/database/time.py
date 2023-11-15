
from time import time

def _time_in_ms()->int:
    """Time in miliseconds."""
    return int(time()*1000)

def timestamp()->int: 
    """Timestamp in milliseconds."""
    return _time_in_ms()

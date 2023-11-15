DATA_RETENTION_PERIOD = 3600000 # 1 hour

from time import time as __time
def timestamp()->int: 
    """Timestamp in milliseconds."""
    return int(__time()*1000)


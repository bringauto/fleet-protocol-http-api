from time import time


def _time_in_ms() -> int:
    """Time in miliseconds."""
    return int(time() * 1000)  # pragma: no cover


def timestamp() -> int:
    """UNIX Timestamp in milliseconds."""
    return _time_in_ms()

from typing import Callable
import threading


def run_in_threads(*functions: Callable[[], None]) -> None:
    threads = [threading.Thread(target=f) for f in functions]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

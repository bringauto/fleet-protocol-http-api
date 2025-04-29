import unittest
import time
import requests
from multiprocessing import Process

import server.app as _app


class Test_Server_Failure_During_Waiting_Request(unittest.TestCase):

    def test_the_requests_returns_503_after_the_server_shuts_down(self):
        self.app = _app.get_test_app(
            predef_api_key="test_key", db_location="test_db.db", base_url="/v2/protocol/"
        )

        def server_lifetime():
            # this is a shutdown request
            process = Process(target=self.app.app._app.run)
            process.start()
            time.sleep(1)
            process.terminate()
            process.join()

        server_process = Process(target=server_lifetime)
        server_process.start()
        time.sleep(0.1)

        # this is a succesfull request during the server being up
        response = requests.get("http://localhost:5000/v2/protocol/cars?api_key=test_key")
        self.assertEqual(response.status_code, 200)

        # this is a request that should fail with 503
        request_process = Process(
            target=requests.get,
            args=("http://localhost:5000/v2/protocol/cars?api_key=test_key&wait=true",),
        )
        request_process.start()
        request_process.join()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

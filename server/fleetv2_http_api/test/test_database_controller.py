import unittest

from flask import json

from fleetv2_http_api.models.connect_to_database_request import ConnectToDatabaseRequest  # noqa: E501
from fleetv2_http_api.test import BaseTestCase


class TestDatabaseController(BaseTestCase):
    """DatabaseController integration test stubs"""

    def test_connect_to_database(self):
        """Test case for connect_to_database

        
        """
        connect_to_database_request = fleetv2_http_api.ConnectToDatabaseRequest()
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/',
            method='PUT',
            headers=headers,
            data=json.dumps(connect_to_database_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()

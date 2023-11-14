import unittest

from flask import json

from fleetv2_http_api.models.car import Car  # noqa: E501
from fleetv2_http_api.test import BaseTestCase


class TestCarController(BaseTestCase):
    """CarController integration test stubs"""

    def test_add_car(self):
        """Test case for add_car

        
        """
        car = {"car_name":"piba09223","company_name":"bringauto"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/cars',
            method='POST',
            headers=headers,
            data=json.dumps(car),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_cars_available(self):
        """Test case for cars_available

        
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/cars',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()

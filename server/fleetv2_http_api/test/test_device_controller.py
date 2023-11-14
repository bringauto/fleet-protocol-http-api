import unittest

from flask import json

from fleetv2_http_api.models.device_id import DeviceId  # noqa: E501
from fleetv2_http_api.models.payload import Payload  # noqa: E501
from fleetv2_http_api.test import BaseTestCase


class TestDeviceController(BaseTestCase):
    """DeviceController integration test stubs"""

    def test_add_device(self):
        """Test case for add_device

        
        """
        device_id = {"module_id":42,"role":"warning_led","name":"Left red LED","type":4}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/{company_name}/{car_name}/available-devices'.format(car_name='auto_123', company_name='company_xyz'),
            method='POST',
            headers=headers,
            data=json.dumps(device_id),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_available_devices(self):
        """Test case for available_devices

        
        """
        query_string = [('module-id', 785)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/{company_name}/{car_name}/available-devices'.format(car_name='auto_123', company_name='company_xyz'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_commands(self):
        """Test case for list_commands

        
        """
        query_string = [('all', false),
                        ('since', 1699262836)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/{company_name}/{car_name}/command/{device_id}'.format(device_id=fleetv2_http_api.DeviceId(), car_name='auto_123', company_name='company_xyz'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_statuses(self):
        """Test case for list_statuses

        
        """
        query_string = [('all', false),
                        ('since', 1699262836)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/{company_name}/{car_name}/status/{device_id}'.format(device_id=fleetv2_http_api.DeviceId(), car_name='auto_123', company_name='company_xyz'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_send_commands(self):
        """Test case for send_commands

        
        """
        payload = {"data":{"main_text":"The device is running."},"type":4,"encoding":"BASE64"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/{company_name}/{car_name}/command/{device_id}'.format(device_id=fleetv2_http_api.DeviceId(), car_name='auto_123', company_name='company_xyz'),
            method='POST',
            headers=headers,
            data=json.dumps(payload),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_send_statuses(self):
        """Test case for send_statuses

        
        """
        payload = {"data":{"main_text":"The device is running."},"type":4,"encoding":"BASE64"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/{company_name}/{car_name}/status/{device_id}'.format(device_id=fleetv2_http_api.DeviceId(), car_name='auto_123', company_name='company_xyz'),
            method='POST',
            headers=headers,
            data=json.dumps(payload),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()

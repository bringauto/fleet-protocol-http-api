# coding: utf-8

"""
    Fleet v2 HTTP API

    Development version of a the API

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from http_api_client.models.payload import Payload  # noqa: E501

class TestPayload(unittest.TestCase):
    """Payload unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> Payload:
        """Test Payload
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `Payload`
        """
        model = Payload()  # noqa: E501
        if include_optional:
            return Payload(
                type = 4,
                encoding = 'BASE64',
                data = {"main_text":"The device is running."}
            )
        else:
            return Payload(
        )
        """

    def testPayload(self):
        """Test Payload"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
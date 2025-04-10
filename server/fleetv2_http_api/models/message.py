from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from server.fleetv2_http_api.models.base_model import Model
from server.fleetv2_http_api.models.device_id import DeviceId
from server.fleetv2_http_api.models.payload import Payload
from server.fleetv2_http_api import util

from server.fleetv2_http_api.models.device_id import DeviceId  # noqa: E501
from server.fleetv2_http_api.models.payload import Payload  # noqa: E501

class Message(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, timestamp=None, device_id=None, payload=None):  # noqa: E501
        """Message - a model defined in OpenAPI

        :param timestamp: The timestamp of this Message.  # noqa: E501
        :type timestamp: int
        :param device_id: The device_id of this Message.  # noqa: E501
        :type device_id: DeviceId
        :param payload: The payload of this Message.  # noqa: E501
        :type payload: Payload
        """
        self.openapi_types = {
            'timestamp': int,
            'device_id': DeviceId,
            'payload': Payload
        }

        self.attribute_map = {
            'timestamp': 'timestamp',
            'device_id': 'device_id',
            'payload': 'payload'
        }

        self._timestamp = timestamp
        self._device_id = device_id
        self._payload = payload

    @classmethod
    def from_dict(cls, dikt) -> 'Message':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Message of this Message.  # noqa: E501
        :rtype: Message
        """
        return util.deserialize_model(dikt, cls)

    @property
    def timestamp(self) -> int:
        """Gets the timestamp of this Message.

        Unix timestamp of the message in milliseconds.  # noqa: E501

        :return: The timestamp of this Message.
        :rtype: int
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp: int):
        """Sets the timestamp of this Message.

        Unix timestamp of the message in milliseconds.  # noqa: E501

        :param timestamp: The timestamp of this Message.
        :type timestamp: int
        """

        self._timestamp = timestamp

    @property
    def device_id(self) -> DeviceId:
        """Gets the device_id of this Message.


        :return: The device_id of this Message.
        :rtype: DeviceId
        """
        return self._device_id

    @device_id.setter
    def device_id(self, device_id: DeviceId):
        """Sets the device_id of this Message.


        :param device_id: The device_id of this Message.
        :type device_id: DeviceId
        """
        if device_id is None:
            raise ValueError("Invalid value for `device_id`, must not be `None`")  # noqa: E501

        self._device_id = device_id

    @property
    def payload(self) -> Payload:
        """Gets the payload of this Message.


        :return: The payload of this Message.
        :rtype: Payload
        """
        return self._payload

    @payload.setter
    def payload(self, payload: Payload):
        """Sets the payload of this Message.


        :param payload: The payload of this Message.
        :type payload: Payload
        """
        if payload is None:
            raise ValueError("Invalid value for `payload`, must not be `None`")  # noqa: E501

        self._payload = payload

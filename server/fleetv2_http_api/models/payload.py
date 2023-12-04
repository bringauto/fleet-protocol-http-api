from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleetv2_http_api.models.base_model import Model
from fleetv2_http_api.models.payload_data import PayloadData
import re
from fleetv2_http_api import util

from fleetv2_http_api.models.payload_data import PayloadData  # noqa: E501
import re  # noqa: E501

class Payload(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, message_type=None, encoding=None, data=None):  # noqa: E501
        """Payload - a model defined in OpenAPI

        :param message_type: The message_type of this Payload.  # noqa: E501
        :type message_type: str
        :param encoding: The encoding of this Payload.  # noqa: E501
        :type encoding: str
        :param data: The data of this Payload.  # noqa: E501
        :type data: PayloadData
        """
        self.openapi_types = {
            'message_type': str,
            'encoding': str,
            'data': PayloadData
        }

        self.attribute_map = {
            'message_type': 'message_type',
            'encoding': 'encoding',
            'data': 'data'
        }

        self._message_type = message_type
        self._encoding = encoding
        self._data = data

    @classmethod
    def from_dict(cls, dikt) -> 'Payload':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Payload of this Payload.  # noqa: E501
        :rtype: Payload
        """
        return util.deserialize_model(dikt, cls)

    @property
    def message_type(self) -> str:
        """Gets the message_type of this Payload.

        Type of the payload  # noqa: E501

        :return: The message_type of this Payload.
        :rtype: str
        """
        return self._message_type

    @message_type.setter
    def message_type(self, message_type: str):
        """Sets the message_type of this Payload.

        Type of the payload  # noqa: E501

        :param message_type: The message_type of this Payload.
        :type message_type: str
        """
        if message_type is not None and not re.search(r'^(STATUS)|(COMMAND)$', message_type):  # noqa: E501
            raise ValueError("Invalid value for `message_type`, must be a follow pattern or equal to `/^(STATUS)|(COMMAND)$/`")  # noqa: E501

        self._message_type = message_type

    @property
    def encoding(self) -> str:
        """Gets the encoding of this Payload.

        Encoding of the payload  # noqa: E501

        :return: The encoding of this Payload.
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding: str):
        """Sets the encoding of this Payload.

        Encoding of the payload  # noqa: E501

        :param encoding: The encoding of this Payload.
        :type encoding: str
        """
        if encoding is not None and not re.search(r'^(JSON)|(BASE64)$', encoding):  # noqa: E501
            raise ValueError("Invalid value for `encoding`, must be a follow pattern or equal to `/^(JSON)|(BASE64)$/`")  # noqa: E501

        self._encoding = encoding

    @property
    def data(self) -> PayloadData:
        """Gets the data of this Payload.


        :return: The data of this Payload.
        :rtype: PayloadData
        """
        return self._data

    @data.setter
    def data(self, data: PayloadData):
        """Sets the data of this Payload.


        :param data: The data of this Payload.
        :type data: PayloadData
        """

        self._data = data

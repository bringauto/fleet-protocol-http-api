from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleetv2_http_api.models.base_model import Model
from fleetv2_http_api.models.device_id import DeviceId
from fleetv2_http_api import util

from fleetv2_http_api.models.device_id import DeviceId  # noqa: E501

class Module(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, device_list=None):  # noqa: E501
        """Module - a model defined in OpenAPI

        :param id: The id of this Module.  # noqa: E501
        :type id: int
        :param device_list: The device_list of this Module.  # noqa: E501
        :type device_list: List[DeviceId]
        """
        self.openapi_types = {
            'id': int,
            'device_list': List[DeviceId]
        }

        self.attribute_map = {
            'id': 'id',
            'device_list': 'device-list'
        }

        self._id = id
        self._device_list = device_list

    @classmethod
    def from_dict(cls, dikt) -> 'Module':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Module of this Module.  # noqa: E501
        :rtype: Module
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> int:
        """Gets the id of this Module.

        A general integer Id  # noqa: E501

        :return: The id of this Module.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """Sets the id of this Module.

        A general integer Id  # noqa: E501

        :param id: The id of this Module.
        :type id: int
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501
        if id is not None and id < 0:  # noqa: E501
            raise ValueError("Invalid value for `id`, must be a value greater than or equal to `0`")  # noqa: E501

        self._id = id

    @property
    def device_list(self) -> List[DeviceId]:
        """Gets the device_list of this Module.


        :return: The device_list of this Module.
        :rtype: List[DeviceId]
        """
        return self._device_list

    @device_list.setter
    def device_list(self, device_list: List[DeviceId]):
        """Sets the device_list of this Module.


        :param device_list: The device_list of this Module.
        :type device_list: List[DeviceId]
        """
        if device_list is None:
            raise ValueError("Invalid value for `device_list`, must not be `None`")  # noqa: E501

        self._device_list = device_list

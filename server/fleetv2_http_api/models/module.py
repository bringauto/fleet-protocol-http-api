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

    def __init__(self, module_id=None, device_list=None):  # noqa: E501
        """Module - a model defined in OpenAPI

        :param module_id: The module_id of this Module.  # noqa: E501
        :type module_id: int
        :param device_list: The device_list of this Module.  # noqa: E501
        :type device_list: List[DeviceId]
        """
        self.openapi_types = {
            'module_id': int,
            'device_list': List[DeviceId]
        }

        self.attribute_map = {
            'module_id': 'module_id',
            'device_list': 'device_list'
        }

        self._module_id = module_id
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
    def module_id(self) -> int:
        """Gets the module_id of this Module.

        Id (unsigned integer) of the module.  # noqa: E501

        :return: The module_id of this Module.
        :rtype: int
        """
        return self._module_id

    @module_id.setter
    def module_id(self, module_id: int):
        """Sets the module_id of this Module.

        Id (unsigned integer) of the module.  # noqa: E501

        :param module_id: The module_id of this Module.
        :type module_id: int
        """
        if module_id is not None and module_id < 0:  # noqa: E501
            raise ValueError("Invalid value for `module_id`, must be a value greater than or equal to `0`")  # noqa: E501

        self._module_id = module_id

    @property
    def device_list(self) -> List[DeviceId]:
        """Gets the device_list of this Module.

        List of Ids of devices contained in the module.  # noqa: E501

        :return: The device_list of this Module.
        :rtype: List[DeviceId]
        """
        return self._device_list

    @device_list.setter
    def device_list(self, device_list: List[DeviceId]):
        """Sets the device_list of this Module.

        List of Ids of devices contained in the module.  # noqa: E501

        :param device_list: The device_list of this Module.
        :type device_list: List[DeviceId]
        """

        self._device_list = device_list
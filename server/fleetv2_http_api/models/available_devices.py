from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from server.fleetv2_http_api.models.base_model import Model
from server.fleetv2_http_api.models.device_id import DeviceId
from server.fleetv2_http_api.models.module import Module
from server.fleetv2_http_api import util

from server.fleetv2_http_api.models.device_id import DeviceId  # noqa: E501
from server.fleetv2_http_api.models.module import Module  # noqa: E501


class AvailableDevices(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, module_id=None, device_list=None):  # noqa: E501
        """AvailableDevices - a model defined in OpenAPI

        :param module_id: The module_id of this AvailableDevices.  # noqa: E501
        :type module_id: int
        :param device_list: The device_list of this AvailableDevices.  # noqa: E501
        :type device_list: List[DeviceId]
        """
        self.openapi_types = {"module_id": int, "device_list": List[DeviceId]}

        self.attribute_map = {"module_id": "module_id", "device_list": "device_list"}

        self._module_id = module_id
        self._device_list = device_list

    @classmethod
    def from_dict(cls, dikt) -> "AvailableDevices":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The AvailableDevices of this AvailableDevices.  # noqa: E501
        :rtype: AvailableDevices
        """
        return util.deserialize_model(dikt, cls)

    @property
    def module_id(self) -> int:
        """Gets the module_id of this AvailableDevices.

        Id (unsigned integer) of the module.  # noqa: E501

        :return: The module_id of this AvailableDevices.
        :rtype: int
        """
        return self._module_id

    @module_id.setter
    def module_id(self, module_id: int):
        """Sets the module_id of this AvailableDevices.

        Id (unsigned integer) of the module.  # noqa: E501

        :param module_id: The module_id of this AvailableDevices.
        :type module_id: int
        """
        if module_id is None:
            raise ValueError("Invalid value for `module_id`, must not be `None`")  # noqa: E501
        if module_id is not None and module_id < 0:  # noqa: E501
            raise ValueError(
                "Invalid value for `module_id`, must be a value greater than or equal to `0`"
            )  # noqa: E501

        self._module_id = module_id

    @property
    def device_list(self) -> List[DeviceId]:
        """Gets the device_list of this AvailableDevices.

        List of Ids of devices contained in the module.  # noqa: E501

        :return: The device_list of this AvailableDevices.
        :rtype: List[DeviceId]
        """
        return self._device_list

    @device_list.setter
    def device_list(self, device_list: List[DeviceId]):
        """Sets the device_list of this AvailableDevices.

        List of Ids of devices contained in the module.  # noqa: E501

        :param device_list: The device_list of this AvailableDevices.
        :type device_list: List[DeviceId]
        """
        if device_list is None:
            raise ValueError("Invalid value for `device_list`, must not be `None`")  # noqa: E501

        self._device_list = device_list

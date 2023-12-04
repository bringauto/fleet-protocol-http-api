from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleetv2_http_api.models.base_model import Model
import re
from fleetv2_http_api import util

import re  # noqa: E501

class DeviceId(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, module_id=None, type=None, role=None, name=None):  # noqa: E501
        """DeviceId - a model defined in OpenAPI

        :param module_id: The module_id of this DeviceId.  # noqa: E501
        :type module_id: int
        :param type: The type of this DeviceId.  # noqa: E501
        :type type: int
        :param role: The role of this DeviceId.  # noqa: E501
        :type role: str
        :param name: The name of this DeviceId.  # noqa: E501
        :type name: str
        """
        self.openapi_types = {
            'module_id': int,
            'type': int,
            'role': str,
            'name': str
        }

        self.attribute_map = {
            'module_id': 'module_id',
            'type': 'type',
            'role': 'role',
            'name': 'name'
        }

        self._module_id = module_id
        self._type = type
        self._role = role
        self._name = name

    @classmethod
    def from_dict(cls, dikt) -> 'DeviceId':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The DeviceId of this DeviceId.  # noqa: E501
        :rtype: DeviceId
        """
        return util.deserialize_model(dikt, cls)

    @property
    def module_id(self) -> int:
        """Gets the module_id of this DeviceId.

        Id (unsigned integer) of the module containing the device.  # noqa: E501

        :return: The module_id of this DeviceId.
        :rtype: int
        """
        return self._module_id

    @module_id.setter
    def module_id(self, module_id: int):
        """Sets the module_id of this DeviceId.

        Id (unsigned integer) of the module containing the device.  # noqa: E501

        :param module_id: The module_id of this DeviceId.
        :type module_id: int
        """
        if module_id is not None and module_id < 0:  # noqa: E501
            raise ValueError("Invalid value for `module_id`, must be a value greater than or equal to `0`")  # noqa: E501

        self._module_id = module_id

    @property
    def type(self) -> int:
        """Gets the type of this DeviceId.

        Unsigned integer.  # noqa: E501

        :return: The type of this DeviceId.
        :rtype: int
        """
        return self._type

    @type.setter
    def type(self, type: int):
        """Sets the type of this DeviceId.

        Unsigned integer.  # noqa: E501

        :param type: The type of this DeviceId.
        :type type: int
        """
        if type is not None and type < 0:  # noqa: E501
            raise ValueError("Invalid value for `type`, must be a value greater than or equal to `0`")  # noqa: E501

        self._type = type

    @property
    def role(self) -> str:
        """Gets the role of this DeviceId.

        String description of the device role. It follows pattern ^[a-z0-9_]+$.  # noqa: E501

        :return: The role of this DeviceId.
        :rtype: str
        """
        return self._role

    @role.setter
    def role(self, role: str):
        """Sets the role of this DeviceId.

        String description of the device role. It follows pattern ^[a-z0-9_]+$.  # noqa: E501

        :param role: The role of this DeviceId.
        :type role: str
        """
        if role is not None and not re.search(r'^[a-z0-9_]+$', role):  # noqa: E501
            raise ValueError("Invalid value for `role`, must be a follow pattern or equal to `/^[a-z0-9_]+$/`")  # noqa: E501

        self._role = role

    @property
    def name(self) -> str:
        """Gets the name of this DeviceId.

        UTF-8 encoded string.  # noqa: E501

        :return: The name of this DeviceId.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this DeviceId.

        UTF-8 encoded string.  # noqa: E501

        :param name: The name of this DeviceId.
        :type name: str
        """

        self._name = name

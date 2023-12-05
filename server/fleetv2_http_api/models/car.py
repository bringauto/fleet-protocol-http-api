from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from fleetv2_http_api.models.base_model import Model
import re
from fleetv2_http_api import util

import re  # noqa: E501

class Car(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, company_name=None, car_name=None):  # noqa: E501
        """Car - a model defined in OpenAPI

        :param company_name: The company_name of this Car.  # noqa: E501
        :type company_name: str
        :param car_name: The car_name of this Car.  # noqa: E501
        :type car_name: str
        """
        self.openapi_types = {
            'company_name': str,
            'car_name': str
        }

        self.attribute_map = {
            'company_name': 'company_name',
            'car_name': 'car_name'
        }

        self._company_name = company_name
        self._car_name = car_name

    @classmethod
    def from_dict(cls, dikt) -> 'Car':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Car of this Car.  # noqa: E501
        :rtype: Car
        """
        return util.deserialize_model(dikt, cls)

    @property
    def company_name(self) -> str:
        """Gets the company_name of this Car.

        Name of the company, following a pattern ^[0-9a-z_]+$  # noqa: E501

        :return: The company_name of this Car.
        :rtype: str
        """
        return self._company_name

    @company_name.setter
    def company_name(self, company_name: str):
        """Sets the company_name of this Car.

        Name of the company, following a pattern ^[0-9a-z_]+$  # noqa: E501

        :param company_name: The company_name of this Car.
        :type company_name: str
        """
        if company_name is not None and not re.search(r'^[0-9a-z_]+$', company_name):  # noqa: E501
            raise ValueError("Invalid value for `company_name`, must be a follow pattern or equal to `/^[0-9a-z_]+$/`")  # noqa: E501

        self._company_name = company_name

    @property
    def car_name(self) -> str:
        """Gets the car_name of this Car.

        Name of the Car, following a pattern ^[0-9a-z_]+$  # noqa: E501

        :return: The car_name of this Car.
        :rtype: str
        """
        return self._car_name

    @car_name.setter
    def car_name(self, car_name: str):
        """Sets the car_name of this Car.

        Name of the Car, following a pattern ^[0-9a-z_]+$  # noqa: E501

        :param car_name: The car_name of this Car.
        :type car_name: str
        """
        if car_name is not None and not re.search(r'^[0-9a-z_]+$', car_name):  # noqa: E501
            raise ValueError("Invalid value for `car_name`, must be a follow pattern or equal to `/^[0-9a-z_]+$/`")  # noqa: E501

        self._car_name = car_name

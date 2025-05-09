import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api.models.available_devices import AvailableDevices  # noqa: E501
from fleetv2_http_api import util


def available_devices(company_name, car_name, module_id=None):  # noqa: E501
    """available_devices

    Return device Ids for all devices available for contained in the specified car.&lt;br&gt; For a single car module, the device Ids are returned as an object containing module Id and the list of device Ids. &lt;br&gt; If a module Id is specified, only a single such object is returned. &lt;br&gt; Otherwise, a list of such objects is returned, one for each module contained in the car. &lt;br&gt; # noqa: E501

    :param company_name: Name of the company, following a pattern ^[0-9a-z_]+$.
    :type company_name: str
    :param car_name: Name of the Car, following a pattern ^[0-9a-z_]+$.
    :type car_name: str
    :param module_id: An Id of module, an unsigned integer.
    :type module_id: int

    :rtype: Union[AvailableDevices, Tuple[AvailableDevices, int], Tuple[AvailableDevices, int, Dict[str, str]]
    """
    return 'do some magic!'

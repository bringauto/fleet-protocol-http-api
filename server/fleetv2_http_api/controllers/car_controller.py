import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from fleetv2_http_api import util


def available_cars():  # noqa: E501
    """available_cars

    Return list of available cars for all companies registered in the database.&lt;br&gt; Each item list has the format: &#39;&amp;lt;company name&amp;gt;_&amp;lt;car name&amp;gt;&#39;. # noqa: E501


    :rtype: Union[List[str], Tuple[List[str], int], Tuple[List[str], int, Dict[str, str]]
    """
    return 'do some magic!'

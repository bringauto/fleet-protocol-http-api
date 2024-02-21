import sys

sys.path.append("source")


from copy import deepcopy
from fleetv2_http_api.models.device_id import DeviceId


Device_Ids = dict[str, dict[str, dict[int, dict[str, DeviceId]]]]


_device_ids: Device_Ids = {}


def device_ids() -> Device_Ids:
    """Return a deep copy of the device_ids dictionary.""" ""
    return deepcopy(_device_ids)


def clear_device_ids() -> None:
    """Clear the whole device_ids dictionary.""" ""
    _device_ids.clear()


def remove_device_id(company_name: str, car_name: str, device_id: DeviceId | str) -> None:
    """Remove a device id from its module dict in the device_ids dictionary."""
    if isinstance(device_id, DeviceId):
        sdevice_id = serialized_device_id(device_id)
        module_id = device_id.module_id
    else:
        sdevice_id = device_id
        module_id = int(device_id.split("_")[0])
    _device_ids[company_name][car_name][module_id].pop(sdevice_id)


def clean_up_disconnected_cars_and_modules() -> None:
    """Remove empty modules, cars and companies from the device_ids dictionary."""
    for company_name in _device_ids:
        for car_name in _device_ids[company_name]:
            empty_modules = [
                module_id
                for module_id in _device_ids[company_name][car_name].keys()
                if not _device_ids[company_name][car_name][module_id]
            ]
            for module_id in empty_modules:
                _device_ids[company_name][car_name].pop(module_id)

        cars_without_modules = [
            car for car in _device_ids[company_name].keys() if not _device_ids[company_name][car]
        ]
        for car in cars_without_modules:
            _device_ids[company_name].pop(car)

    companies_without_cars = [company for company in _device_ids.keys() if not _device_ids[company]]
    for company in companies_without_cars:
        _device_ids.pop(company)


def store_device_id_if_new(company_name: str, car_name: str, device_id: DeviceId) -> bool:
    """
    Add a device id to the device_ids dictionary if it is not already there.
    Returns True if the device id was stored, False otherwise.
    """
    sdevice_id = serialized_device_id(device_id)
    if company_name not in _device_ids:
        _device_ids[company_name] = dict()

    if car_name not in _device_ids[company_name]:
        _device_ids[company_name][car_name] = dict()

    if device_id.module_id not in _device_ids[company_name][car_name]:
        _device_ids[company_name][car_name][device_id.module_id] = dict()

    if sdevice_id not in _device_ids[company_name][car_name][device_id.module_id]:
        _device_ids[company_name][car_name][device_id.module_id][sdevice_id] = device_id
        return True

    return False


def serialized_device_id(device_id: DeviceId) -> str:
    return f"{device_id.module_id}_{device_id.type}_{device_id.role}"

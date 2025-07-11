from __future__ import annotations
import dataclasses
from collections import defaultdict
from copy import deepcopy

from server.fleetv2_http_api.models.device_id import DeviceId  # type: ignore
from server.database.models import AdminDB  # type: ignore


_loaded_admins: list[AdminDB] = []
_connected_cars: dict[str, dict[str, ConnectedCar]] = defaultdict(dict)


def clear_loaded_admins() -> None:
    global _loaded_admins
    _loaded_admins.clear()


def get_loaded_admins() -> list[AdminDB]:
    return _loaded_admins.copy()


def store_admin(admin: AdminDB) -> None:
    _loaded_admins.append(admin)


@dataclasses.dataclass(frozen=True)
class ConnectedModule:
    id: int
    device_ids: dict[str, DeviceId] = dataclasses.field(default_factory=dict)

    @property
    def sdevice_ids(self) -> list[str]:
        return [device_id for device_id in self.device_ids]

    def add_device(self, device_id: DeviceId) -> bool:
        """Add a device id to the device_ids list.

        Returns True if the device id was stored, False otherwise.
        """
        sdevice_id = serialized_device_id(device_id)
        if sdevice_id not in self.device_ids:
            self.device_ids[sdevice_id] = device_id
            return True
        return False

    def is_connected(self, device_id: DeviceId) -> bool:
        """Check if a device id is connected to this module."""
        sdevice_id = serialized_device_id(device_id)
        return sdevice_id in self.device_ids

    def remove_device(self, device_id: DeviceId) -> bool:
        """Remove a device id from the device_ids list.

        Returns True if the device id was removed, False otherwise.
        """
        sdevice_id = serialized_device_id(device_id)
        if sdevice_id in self.device_ids:
            del self.device_ids[sdevice_id]
            return True
        return False


@dataclasses.dataclass(frozen=True)
class ConnectedCar:
    company_name: str
    car_name: str
    timestamp: int
    modules: dict[int, ConnectedModule] = dataclasses.field(default_factory=dict)

    def add_device(self, device_id: DeviceId) -> bool:
        """Add a device id to the device_ids dictionary.

        Returns True if the device id was stored, False otherwise.
        """
        if not device_id.module_id in self.modules:
            self.modules[device_id.module_id] = ConnectedModule(id=device_id.module_id)
        return self.modules[device_id.module_id].add_device(device_id)

    def is_connected(self, device_id: DeviceId) -> bool:
        """Check if a device id is connected to this car."""
        return device_id.module_id in self.modules and self.modules[
            device_id.module_id
        ].is_connected(device_id)

    def remove_device(self, device_id: DeviceId) -> bool:
        """Remove a device id from its module dict in the device_ids dictionary.

        Returns True if the device id was removed, False otherwise.
        """
        if device_id.module_id in self.modules:
            self.modules[device_id.module_id].remove_device(device_id)
            if not self.modules[device_id.module_id].device_ids:
                self.modules.pop(device_id.module_id)
            return True
        return False


def add_car(company_name: str, car_name: str, timestamp: int) -> bool:
    """Add a car to the device_ids dictionary if it is not already there.

    Returns True if the car was added, False otherwise.
    """
    if company_name not in _connected_cars:
        _connected_cars[company_name] = {}
    if car_name not in _connected_cars[company_name]:
        _connected_cars[company_name][car_name] = ConnectedCar(
            company_name=company_name, car_name=car_name, timestamp=timestamp
        )
        return True
    return False


def add_device(company_name: str, car_name: str, device_id: DeviceId) -> bool:
    """Add a device id to the device_ids dictionary.

    Returns True if the device id was stored, False otherwise.
    """
    if not is_car_connected(company_name, car_name):
        return False
    return _connected_cars[company_name][car_name].add_device(device_id)


def connected_cars() -> dict[str, dict[str, ConnectedCar]]:
    """Return a deep copy of the device_ids dictionary.""" ""
    return deepcopy(_connected_cars)


def is_car_connected(company_name: str, car_name: str) -> bool:
    """Check if a car is connected."""
    return company_name in _connected_cars and car_name in _connected_cars[company_name]


def clear_connected_cars() -> None:
    """Clear the whole device_ids dictionary.""" ""
    _connected_cars.clear()


def remove_connected_device(company_name: str, car_name: str, device_id: DeviceId) -> None:
    """Remove a device id from its module dict in the device_ids dictionary."""
    _connected_cars[company_name][car_name].remove_device(device_id)


def clean_up_disconnected_cars_and_modules() -> None:
    """Remove empty modules, cars and companies from the device_ids dictionary."""
    for company in _connected_cars:
        for car in _connected_cars[company]:
            empty_modules: list[ConnectedModule] = []
            for module in _connected_cars[company][car].modules.values():
                if not module.device_ids:
                    empty_modules.append(module)
            for module in empty_modules:
                _connected_cars[company][car].modules.pop(module.id)

        cars_without_modules = [
            car
            for car in _connected_cars[company].keys()
            if not _connected_cars[company][car].modules
        ]
        for car in cars_without_modules:
            _connected_cars[company].pop(car)

    companies_without_cars = [
        company for company in _connected_cars.keys() if not _connected_cars[company]
    ]
    for company in companies_without_cars:
        _connected_cars.pop(company)


def serialized_device_id(device_id: DeviceId) -> str:
    return f"{device_id.module_id}_{device_id.type}_{device_id.role}"

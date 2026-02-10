from enum import Enum
from typing import Any

from flask.json.provider import DefaultJSONProvider

from server.fleetv2_http_api.models.base_model import Model


def _serialize(obj: Any) -> Any:
    """Recursively serialize Model objects and Enums to JSON-compatible types."""
    if isinstance(obj, Model):
        result = {}
        for attr in obj.openapi_types:
            value = getattr(obj, attr)
            if value is None:
                continue
            key = obj.attribute_map[attr]
            result[key] = _serialize(value)
        return result
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, list):
        return [_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj


class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON provider for Flask 2.3+ that handles OpenAPI models."""

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        obj = _serialize(obj)
        return super().dumps(obj, **kwargs)

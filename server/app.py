from __future__ import annotations
from typing import Any
import os

from flask.testing import FlaskClient as _FlaskClient  # type: ignore
import connexion as _connexion  # type: ignore
from sqlalchemy.orm import Session as _Session

from database.connection import ( # type: ignore
    get_connection_source as _get_connection_source,
    set_test_db_connection as _set_test_db_connection,
    create_all_tables as _create_all_tables
)
from fleetv2_http_api.impl.controllers import ( # type: ignore
    set_command_wait_timeout_s,
    set_status_wait_timeout_s
)

from fleetv2_http_api.encoder import JSONEncoder  # type: ignore
from database.security import _AdminBase as _AdminBase  # type: ignore

# Keep the following import to make all the tables be created by the get_test_app function
from database.device_ids import clear_device_ids as _clear_device_ids  # type: ignore


def get_app() -> _connexion.FlaskApp:
    app = _connexion.App(__name__, specification_dir="fleetv2_http_api/openapi/")
    app.app.json_encoder = JSONEncoder
    app.add_api("openapi.yaml")
    return app


class TestApp:
    def __init__(self, base_url: str, api_key: str = "", db_location: str = "") -> None:
        self._app = get_app()
        self._flask_app = self._TestFlaskApp(api_key, self._app.app, base_url)
        self._db_location = db_location

    @property
    def app(self) -> _TestFlaskApp:
        return self._flask_app

    def clear_all(self) -> None:
        if self._db_location != "" and os.path.isfile(self._db_location):
            os.remove(self._db_location)
        _clear_device_ids()

    class _TestFlaskApp:
        def __init__(self, api_key, flask_app, base_url: str, *args, **kwargs) -> None:
            self._app = flask_app
            self._api_key = api_key
            self._base_url = base_url

        def test_client(self) -> _FlaskClient:
            return TestApp._TestClient(self._app, self._api_key, base_url=self._base_url)


    class _TestClient(_FlaskClient):
        def __init__(self, application, api_key: str, base_url: str, *args, **kwargs) -> None:
            super().__init__(application, *args, **kwargs)
            self._key = api_key
            self._base_url = base_url

        def get(self, url: str, *args, **kwargs) -> Any:
            url = self._construct_url(url)
            return super().get(url, *args, **kwargs)

        def head(self, url: str, *args, **kwargs) -> Any:
            url = self._construct_url(url)
            return super().head(url, *args, **kwargs)

        def post(self, url: str, *args, **kwargs) -> Any:
            url = self._construct_url(url)
            return super().post(url, *args, **kwargs)

        def put(self, url: str, *args, **kwargs) -> Any:
            url = self._construct_url(url)
            return super().put(url, *args, **kwargs)

        def delete(self, url: str, *args, **kwargs) -> Any:
            url = self._construct_url(url)
            return super().delete(url, *args, **kwargs)


        def _construct_url(self, uri: str) -> str:
            uri = self._prepend_base_url(uri)
            return self._insert_key(uri)

        def _prepend_base_url(self, url: str) -> str:
            if not url.startswith("/"):
                url = "/" + url
            url = (self._base_url + url).replace("//", "/")
            return url

        def _insert_key(self, uri: str) -> str:
            if "?" in uri:
                uri_base, query_params = uri.split("?")
                return uri_base + f"?api_key={self._key}" + "&" + query_params
            else:
                return uri + f"?api_key={self._key}"


def get_test_app(
    predef_api_key: str = "",
    db_location: str = "",
    db_name: str = "",
    request_timeout_s: float = 1,
    remove_existing_db_file: bool = True,
    base_url: str = ""
) -> TestApp:
    """Creates a test app that can be used for testing purposes.

    It enables to surpass the API key verification by providing a predefined API key.

    If the `predef_api_key` is left empty, no authentication is required.
    The API key can be set to any value, that can be used as a value for 'api_key'
    query parameter in the API calls.
    """

    if os.path.isfile(db_location):
        if remove_existing_db_file:
            os.remove(db_location)
        else:
            raise ValueError(
                f"The file {db_location} already exists. Please provide a different location."
            )
    _set_test_db_connection("/" + db_location, db_name)
    set_command_wait_timeout_s(request_timeout_s)
    set_status_wait_timeout_s(request_timeout_s)
    source = _get_connection_source()
    _create_all_tables(source)
    with _Session(source) as session:
        admin = _AdminBase(name="test_key", key=predef_api_key)
        session.add(admin)
        session.commit()
    return TestApp(base_url, predef_api_key, db_location)

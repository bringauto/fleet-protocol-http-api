# coding: utf-8

"""
    Fleet v2 HTTP API

    Development version of a the API

    The version of the OpenAPI document: 0.1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import re  # noqa: F401
import io
import warnings

from pydantic import validate_arguments, ValidationError

from typing_extensions import Annotated
from pydantic import Field, StrictBool, StrictInt, conint, conlist

from typing import Any, List, Optional

from http_api_client.models.device_id import DeviceId
from http_api_client.models.payload import Payload

from http_api_client.api_client import ApiClient
from http_api_client.api_response import ApiResponse
from http_api_client.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)


class DeviceApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client

    @validate_arguments
    def available_devices(self, module_id : Annotated[Optional[Any], Field(description="An Id of module.")] = None, **kwargs) -> List[DeviceId]:  # noqa: E501
        """available_devices  # noqa: E501

        Returns list of available devices for the whole car or a single module.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.available_devices(module_id, async_req=True)
        >>> result = thread.get()

        :param module_id: An Id of module.
        :type module_id: object
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: List[DeviceId]
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the available_devices_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.available_devices_with_http_info(module_id, **kwargs)  # noqa: E501

    @validate_arguments
    def available_devices_with_http_info(self, module_id : Annotated[Optional[Any], Field(description="An Id of module.")] = None, **kwargs) -> ApiResponse:  # noqa: E501
        """available_devices  # noqa: E501

        Returns list of available devices for the whole car or a single module.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.available_devices_with_http_info(module_id, async_req=True)
        >>> result = thread.get()

        :param module_id: An Id of module.
        :type module_id: object
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(List[DeviceId], status_code(int), headers(HTTPHeaderDict))
        """

        _hosts = [
            'http://localhost:8080/{company-name}/{car-name}'
        ]
        _host = _hosts[0]
        if kwargs.get('_host_index'):
            _host_index = int(kwargs.get('_host_index'))
            if _host_index < 0 or _host_index >= len(_hosts):
                raise ApiValueError(
                    "Invalid host index. Must be 0 <= index < %s"
                    % len(_host)
                )
            _host = _hosts[_host_index]
        _params = locals()

        _all_params = [
            'module_id'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params and _key != "_host_index":
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method available_devices" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}

        # process the query parameters
        _query_params = []
        if _params.get('module_id') is not None:  # noqa: E501
            _query_params.append(('module-id', _params['module_id']))

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {
            '200': "List[DeviceId]",
            '500': None,
        }

        return self.api_client.call_api(
            '/available-devices', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            _host=_host,
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @validate_arguments
    def list_commands(self, device_id : Annotated[conint(strict=True, ge=0), Field(..., description="The Id of the Device.")], all : Annotated[Optional[StrictBool], Field(description="If set, the method returns a complete history of statuses/commands.")] = None, since : Annotated[Optional[StrictInt], Field(description="A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.")] = None, **kwargs) -> List[Payload]:  # noqa: E501
        """list_commands  # noqa: E501

        Returns list of the Device Commands.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_commands(device_id, all, since, async_req=True)
        >>> result = thread.get()

        :param device_id: The Id of the Device. (required)
        :type device_id: int
        :param all: If set, the method returns a complete history of statuses/commands.
        :type all: bool
        :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
        :type since: int
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: List[Payload]
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the list_commands_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.list_commands_with_http_info(device_id, all, since, **kwargs)  # noqa: E501

    @validate_arguments
    def list_commands_with_http_info(self, device_id : Annotated[conint(strict=True, ge=0), Field(..., description="The Id of the Device.")], all : Annotated[Optional[StrictBool], Field(description="If set, the method returns a complete history of statuses/commands.")] = None, since : Annotated[Optional[StrictInt], Field(description="A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.")] = None, **kwargs) -> ApiResponse:  # noqa: E501
        """list_commands  # noqa: E501

        Returns list of the Device Commands.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_commands_with_http_info(device_id, all, since, async_req=True)
        >>> result = thread.get()

        :param device_id: The Id of the Device. (required)
        :type device_id: int
        :param all: If set, the method returns a complete history of statuses/commands.
        :type all: bool
        :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
        :type since: int
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(List[Payload], status_code(int), headers(HTTPHeaderDict))
        """

        _hosts = [
            'http://localhost:8080/{company-name}/{car-name}'
        ]
        _host = _hosts[0]
        if kwargs.get('_host_index'):
            _host_index = int(kwargs.get('_host_index'))
            if _host_index < 0 or _host_index >= len(_hosts):
                raise ApiValueError(
                    "Invalid host index. Must be 0 <= index < %s"
                    % len(_host)
                )
            _host = _hosts[_host_index]
        _params = locals()

        _all_params = [
            'device_id',
            'all',
            'since'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params and _key != "_host_index":
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method list_commands" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['device_id']:
            _path_params['device-id'] = _params['device_id']


        # process the query parameters
        _query_params = []
        if _params.get('all') is not None:  # noqa: E501
            _query_params.append(('all', _params['all']))

        if _params.get('since') is not None:  # noqa: E501
            _query_params.append(('since', _params['since']))

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {
            '200': "List[Payload]",
            '500': None,
        }

        return self.api_client.call_api(
            '/command/{device-id}', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            _host=_host,
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @validate_arguments
    def list_statuses(self, device_id : Annotated[conint(strict=True, ge=0), Field(..., description="The Id of the Device.")], all : Annotated[Optional[StrictBool], Field(description="If set, the method returns a complete history of statuses/commands.")] = None, since : Annotated[Optional[StrictInt], Field(description="A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.")] = None, **kwargs) -> List[Payload]:  # noqa: E501
        """list_statuses  # noqa: E501

        It returns list of the Device Statuses.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_statuses(device_id, all, since, async_req=True)
        >>> result = thread.get()

        :param device_id: The Id of the Device. (required)
        :type device_id: int
        :param all: If set, the method returns a complete history of statuses/commands.
        :type all: bool
        :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
        :type since: int
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: List[Payload]
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the list_statuses_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.list_statuses_with_http_info(device_id, all, since, **kwargs)  # noqa: E501

    @validate_arguments
    def list_statuses_with_http_info(self, device_id : Annotated[conint(strict=True, ge=0), Field(..., description="The Id of the Device.")], all : Annotated[Optional[StrictBool], Field(description="If set, the method returns a complete history of statuses/commands.")] = None, since : Annotated[Optional[StrictInt], Field(description="A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.")] = None, **kwargs) -> ApiResponse:  # noqa: E501
        """list_statuses  # noqa: E501

        It returns list of the Device Statuses.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_statuses_with_http_info(device_id, all, since, async_req=True)
        >>> result = thread.get()

        :param device_id: The Id of the Device. (required)
        :type device_id: int
        :param all: If set, the method returns a complete history of statuses/commands.
        :type all: bool
        :param since: A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp.
        :type since: int
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(List[Payload], status_code(int), headers(HTTPHeaderDict))
        """

        _hosts = [
            'http://localhost:8080/{company-name}/{car-name}'
        ]
        _host = _hosts[0]
        if kwargs.get('_host_index'):
            _host_index = int(kwargs.get('_host_index'))
            if _host_index < 0 or _host_index >= len(_hosts):
                raise ApiValueError(
                    "Invalid host index. Must be 0 <= index < %s"
                    % len(_host)
                )
            _host = _hosts[_host_index]
        _params = locals()

        _all_params = [
            'device_id',
            'all',
            'since'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params and _key != "_host_index":
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method list_statuses" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['device_id']:
            _path_params['device-id'] = _params['device_id']


        # process the query parameters
        _query_params = []
        if _params.get('all') is not None:  # noqa: E501
            _query_params.append(('all', _params['all']))

        if _params.get('since') is not None:  # noqa: E501
            _query_params.append(('since', _params['since']))

        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {
            '200': "List[Payload]",
            '500': None,
        }

        return self.api_client.call_api(
            '/status/{device-id}', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            _host=_host,
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @validate_arguments
    def send_commands(self, device_id : Annotated[conint(strict=True, ge=0), Field(..., description="The Id of the Device.")], payload : Annotated[Optional[conlist(Payload)], Field(description="Commands to be executed by the device.")] = None, **kwargs) -> None:  # noqa: E501
        """send_commands  # noqa: E501

        It adds new device Commands.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.send_commands(device_id, payload, async_req=True)
        >>> result = thread.get()

        :param device_id: The Id of the Device. (required)
        :type device_id: int
        :param payload: Commands to be executed by the device.
        :type payload: List[Payload]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: None
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the send_commands_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.send_commands_with_http_info(device_id, payload, **kwargs)  # noqa: E501

    @validate_arguments
    def send_commands_with_http_info(self, device_id : Annotated[conint(strict=True, ge=0), Field(..., description="The Id of the Device.")], payload : Annotated[Optional[conlist(Payload)], Field(description="Commands to be executed by the device.")] = None, **kwargs) -> ApiResponse:  # noqa: E501
        """send_commands  # noqa: E501

        It adds new device Commands.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.send_commands_with_http_info(device_id, payload, async_req=True)
        >>> result = thread.get()

        :param device_id: The Id of the Device. (required)
        :type device_id: int
        :param payload: Commands to be executed by the device.
        :type payload: List[Payload]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: None
        """

        _hosts = [
            'http://localhost:8080/{company-name}/{car-name}'
        ]
        _host = _hosts[0]
        if kwargs.get('_host_index'):
            _host_index = int(kwargs.get('_host_index'))
            if _host_index < 0 or _host_index >= len(_hosts):
                raise ApiValueError(
                    "Invalid host index. Must be 0 <= index < %s"
                    % len(_host)
                )
            _host = _hosts[_host_index]
        _params = locals()

        _all_params = [
            'device_id',
            'payload'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params and _key != "_host_index":
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method send_commands" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['device_id']:
            _path_params['device-id'] = _params['device_id']


        # process the query parameters
        _query_params = []
        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        if _params['payload'] is not None:
            _body_params = _params['payload']

        # set the HTTP header `Content-Type`
        _content_types_list = _params.get('_content_type',
            self.api_client.select_header_content_type(
                ['application/json']))
        if _content_types_list:
                _header_params['Content-Type'] = _content_types_list

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {}

        return self.api_client.call_api(
            '/command/{device-id}', 'POST',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            _host=_host,
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @validate_arguments
    def send_statuses(self, device_id : Annotated[conint(strict=True, ge=0), Field(..., description="The Id of the Device.")], payload : Annotated[Optional[conlist(Payload)], Field(description="Statuses to be send by the device.")] = None, **kwargs) -> None:  # noqa: E501
        """send_statuses  # noqa: E501

        Add statuses received from the Device.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.send_statuses(device_id, payload, async_req=True)
        >>> result = thread.get()

        :param device_id: The Id of the Device. (required)
        :type device_id: int
        :param payload: Statuses to be send by the device.
        :type payload: List[Payload]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: None
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the send_statuses_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.send_statuses_with_http_info(device_id, payload, **kwargs)  # noqa: E501

    @validate_arguments
    def send_statuses_with_http_info(self, device_id : Annotated[conint(strict=True, ge=0), Field(..., description="The Id of the Device.")], payload : Annotated[Optional[conlist(Payload)], Field(description="Statuses to be send by the device.")] = None, **kwargs) -> ApiResponse:  # noqa: E501
        """send_statuses  # noqa: E501

        Add statuses received from the Device.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.send_statuses_with_http_info(device_id, payload, async_req=True)
        >>> result = thread.get()

        :param device_id: The Id of the Device. (required)
        :type device_id: int
        :param payload: Statuses to be send by the device.
        :type payload: List[Payload]
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: None
        """

        _hosts = [
            'http://localhost:8080/{company-name}/{car-name}'
        ]
        _host = _hosts[0]
        if kwargs.get('_host_index'):
            _host_index = int(kwargs.get('_host_index'))
            if _host_index < 0 or _host_index >= len(_hosts):
                raise ApiValueError(
                    "Invalid host index. Must be 0 <= index < %s"
                    % len(_host)
                )
            _host = _hosts[_host_index]
        _params = locals()

        _all_params = [
            'device_id',
            'payload'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params and _key != "_host_index":
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method send_statuses" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['device_id']:
            _path_params['device-id'] = _params['device_id']


        # process the query parameters
        _query_params = []
        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        if _params['payload'] is not None:
            _body_params = _params['payload']

        # set the HTTP header `Content-Type`
        _content_types_list = _params.get('_content_type',
            self.api_client.select_header_content_type(
                ['application/json']))
        if _content_types_list:
                _header_params['Content-Type'] = _content_types_list

        # authentication setting
        _auth_settings = []  # noqa: E501

        _response_types_map = {}

        return self.api_client.call_api(
            '/status/{device-id}', 'POST',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            _host=_host,
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))
# http_api_client.DeviceApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_device**](DeviceApi.md#add_device) | **POST** /{company_name}/{car_name}/available-devices | 
[**available_devices**](DeviceApi.md#available_devices) | **GET** /{company_name}/{car_name}/available-devices | 
[**list_commands**](DeviceApi.md#list_commands) | **GET** /{company_name}/{car_name}/command/{device-id} | 
[**list_statuses**](DeviceApi.md#list_statuses) | **GET** /{company_name}/{car_name}/status/{device-id} | 
[**send_commands**](DeviceApi.md#send_commands) | **POST** /{company_name}/{car_name}/command/{device-id} | 
[**send_statuses**](DeviceApi.md#send_statuses) | **POST** /{company_name}/{car_name}/status/{device-id} | 


# **add_device**
> add_device(car_name, company_name, device_id=device_id)



Add a new device

### Example

```python
import time
import os
import http_api_client
from http_api_client.models.device_id import DeviceId
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    car_name = 'auto_123' # str | Name of the Car
    company_name = 'company_xyz' # str | Name of the company
    device_id = http_api_client.DeviceId() # DeviceId | New device (optional)

    try:
        api_instance.add_device(car_name, company_name, device_id=device_id)
    except Exception as e:
        print("Exception when calling DeviceApi->add_device: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **car_name** | **str**| Name of the Car | 
 **company_name** | **str**| Name of the company | 
 **device_id** | [**DeviceId**](DeviceId.md)| New device | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | New device added |  -  |
**500** | Cannot add device due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **available_devices**
> List[DeviceId] available_devices(car_name, company_name, module_id=module_id)



Returns list of available devices for the whole car or a single module.

### Example

```python
import time
import os
import http_api_client
from http_api_client.models.device_id import DeviceId
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    car_name = 'auto_123' # str | Name of the Car
    company_name = 'company_xyz' # str | Name of the company
    module_id = 785 # object | An Id of module. (optional)

    try:
        api_response = api_instance.available_devices(car_name, company_name, module_id=module_id)
        print("The response of DeviceApi->available_devices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeviceApi->available_devices: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **car_name** | **str**| Name of the Car | 
 **company_name** | **str**| Name of the company | 
 **module_id** | [**object**](.md)| An Id of module. | [optional] 

### Return type

[**List[DeviceId]**](DeviceId.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of available devices. |  -  |
**500** | Cannot display available devices due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_commands**
> List[Payload] list_commands(device_id, car_name, company_name, all=all, since=since)



Returns list of the Device Commands.

### Example

```python
import time
import os
import http_api_client
from http_api_client.models.device_id import DeviceId
from http_api_client.models.payload import Payload
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    device_id = http_api_client.DeviceId() # DeviceId | The Id of the Device.
    car_name = 'auto_123' # str | Name of the Car
    company_name = 'company_xyz' # str | Name of the company
    all = false # bool | If set, the method returns a complete history of statuses/commands. (optional)
    since = 1699262836 # int | A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp. (optional)

    try:
        api_response = api_instance.list_commands(device_id, car_name, company_name, all=all, since=since)
        print("The response of DeviceApi->list_commands:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeviceApi->list_commands: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | [**DeviceId**](.md)| The Id of the Device. | 
 **car_name** | **str**| Name of the Car | 
 **company_name** | **str**| Name of the company | 
 **all** | **bool**| If set, the method returns a complete history of statuses/commands. | [optional] 
 **since** | **int**| A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp. | [optional] 

### Return type

[**List[Payload]**](Payload.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of commands. |  -  |
**500** | The commands cannot be displayed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_statuses**
> List[Payload] list_statuses(device_id, car_name, company_name, all=all, since=since)



It returns list of the Device Statuses.

### Example

```python
import time
import os
import http_api_client
from http_api_client.models.device_id import DeviceId
from http_api_client.models.payload import Payload
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    device_id = http_api_client.DeviceId() # DeviceId | The Id of the Device.
    car_name = 'auto_123' # str | Name of the Car
    company_name = 'company_xyz' # str | Name of the company
    all = false # bool | If set, the method returns a complete history of statuses/commands. (optional)
    since = 1699262836 # int | A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp. (optional)

    try:
        api_response = api_instance.list_statuses(device_id, car_name, company_name, all=all, since=since)
        print("The response of DeviceApi->list_statuses:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeviceApi->list_statuses: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | [**DeviceId**](.md)| The Id of the Device. | 
 **car_name** | **str**| Name of the Car | 
 **company_name** | **str**| Name of the company | 
 **all** | **bool**| If set, the method returns a complete history of statuses/commands. | [optional] 
 **since** | **int**| A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp. | [optional] 

### Return type

[**List[Payload]**](Payload.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of device statuses. |  -  |
**500** | The statuses cannot be displayed due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **send_commands**
> send_commands(device_id, car_name, company_name, payload=payload)



It adds new device Commands.

### Example

```python
import time
import os
import http_api_client
from http_api_client.models.device_id import DeviceId
from http_api_client.models.payload import Payload
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    device_id = http_api_client.DeviceId() # DeviceId | The Id of the Device.
    car_name = 'auto_123' # str | Name of the Car
    company_name = 'company_xyz' # str | Name of the company
    payload = [http_api_client.Payload()] # List[Payload] | Commands to be executed by the device. (optional)

    try:
        api_instance.send_commands(device_id, car_name, company_name, payload=payload)
    except Exception as e:
        print("Exception when calling DeviceApi->send_commands: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | [**DeviceId**](.md)| The Id of the Device. | 
 **car_name** | **str**| Name of the Car | 
 **company_name** | **str**| Name of the company | 
 **payload** | [**List[Payload]**](Payload.md)| Commands to be executed by the device. | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The commands have been sent. |  -  |
**500** | The commands have not been sent due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **send_statuses**
> send_statuses(device_id, car_name, company_name, payload=payload)



Add statuses received from the Device.

### Example

```python
import time
import os
import http_api_client
from http_api_client.models.device_id import DeviceId
from http_api_client.models.payload import Payload
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost:8080"
)


# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    device_id = http_api_client.DeviceId() # DeviceId | The Id of the Device.
    car_name = 'auto_123' # str | Name of the Car
    company_name = 'company_xyz' # str | Name of the company
    payload = [http_api_client.Payload()] # List[Payload] | Statuses to be send by the device. (optional)

    try:
        api_instance.send_statuses(device_id, car_name, company_name, payload=payload)
    except Exception as e:
        print("Exception when calling DeviceApi->send_statuses: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | [**DeviceId**](.md)| The Id of the Device. | 
 **car_name** | **str**| Name of the Car | 
 **company_name** | **str**| Name of the company | 
 **payload** | [**List[Payload]**](Payload.md)| Statuses to be send by the device. | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The statuses have been sent. |  -  |
**500** | The statuses could not been sent due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


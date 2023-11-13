# http_api_client.DeviceApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**available_devices**](DeviceApi.md#available_devices) | **GET** /{car_name}/available-devices | 
[**list_commands**](DeviceApi.md#list_commands) | **GET** /{car_name}/command/{device-id} | 
[**list_statuses**](DeviceApi.md#list_statuses) | **GET** /{car_name}/status/{device-id} | 
[**send_commands**](DeviceApi.md#send_commands) | **POST** /{car_name}/command/{device-id} | 
[**send_statuses**](DeviceApi.md#send_statuses) | **POST** /{car_name}/status/{device-id} | 


# **available_devices**
> List[DeviceId] available_devices(car_name, module_id=module_id)



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
    car_name = 56 # int | Name of the Car
    module_id = 785 # object | An Id of module. (optional)

    try:
        api_response = api_instance.available_devices(car_name, module_id=module_id)
        print("The response of DeviceApi->available_devices:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeviceApi->available_devices: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **car_name** | **int**| Name of the Car | 
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
> List[Payload] list_commands(device_id, car_name, all=all, since=since)



Returns list of the Device Commands.

### Example

```python
import time
import os
import http_api_client
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
    device_id = 45 # int | The Id of the Device.
    car_name = 56 # int | Name of the Car
    all = false # bool | If set, the method returns a complete history of statuses/commands. (optional)
    since = 1699262836 # int | A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp. (optional)

    try:
        api_response = api_instance.list_commands(device_id, car_name, all=all, since=since)
        print("The response of DeviceApi->list_commands:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeviceApi->list_commands: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **int**| The Id of the Device. | 
 **car_name** | **int**| Name of the Car | 
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
> List[Payload] list_statuses(device_id, car_name, all=all, since=since)



It returns list of the Device Statuses.

### Example

```python
import time
import os
import http_api_client
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
    device_id = 45 # int | The Id of the Device.
    car_name = 56 # int | Name of the Car
    all = false # bool | If set, the method returns a complete history of statuses/commands. (optional)
    since = 1699262836 # int | A Unix timestamp; if specified, the method returns all device statuses/commands inclusivelly older than value of specified timestamp. (optional)

    try:
        api_response = api_instance.list_statuses(device_id, car_name, all=all, since=since)
        print("The response of DeviceApi->list_statuses:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeviceApi->list_statuses: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **int**| The Id of the Device. | 
 **car_name** | **int**| Name of the Car | 
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
> send_commands(device_id, car_name, payload=payload)



It adds new device Commands.

### Example

```python
import time
import os
import http_api_client
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
    device_id = 45 # int | The Id of the Device.
    car_name = 56 # int | Name of the Car
    payload = [http_api_client.Payload()] # List[Payload] | Commands to be executed by the device. (optional)

    try:
        api_instance.send_commands(device_id, car_name, payload=payload)
    except Exception as e:
        print("Exception when calling DeviceApi->send_commands: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **int**| The Id of the Device. | 
 **car_name** | **int**| Name of the Car | 
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
> send_statuses(device_id, car_name, payload=payload)



Add statuses received from the Device.

### Example

```python
import time
import os
import http_api_client
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
    device_id = 45 # int | The Id of the Device.
    car_name = 56 # int | Name of the Car
    payload = [http_api_client.Payload()] # List[Payload] | Statuses to be send by the device. (optional)

    try:
        api_instance.send_statuses(device_id, car_name, payload=payload)
    except Exception as e:
        print("Exception when calling DeviceApi->send_statuses: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **device_id** | **int**| The Id of the Device. | 
 **car_name** | **int**| Name of the Car | 
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


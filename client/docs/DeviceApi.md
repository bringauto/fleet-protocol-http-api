# http_api_client.DeviceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_commands**](DeviceApi.md#list_commands) | **GET** /{company_name}/{car_name}/command/{sdevice_id} | 
[**list_statuses**](DeviceApi.md#list_statuses) | **GET** /{company_name}/{car_name}/status/{sdevice_id} | 
[**send_commands**](DeviceApi.md#send_commands) | **POST** /{company_name}/{car_name}/command/{sdevice_id} | 
[**send_statuses**](DeviceApi.md#send_statuses) | **POST** /{company_name}/{car_name}/status/{sdevice_id} | 


# **list_commands**
> List[Message] list_commands(company_name, car_name, sdevice_id, all_available=all_available, since=since)



Returns list of the Device Commands.

### Example

* Api Key Authentication (ApiKeyAuth):
```python
import time
import os
import http_api_client
from http_api_client.models.message import Message
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiKeyAuth
configuration.api_key['ApiKeyAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiKeyAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    company_name = 'test_company' # str | Name of the company, following a pattern '^[0-9a-z_]+$'.
    car_name = 'test_car' # str | Name of the Car, following a pattern '^[0-9a-z_]+$'.
    sdevice_id = '47_2_test_device' # str | The Id of the Device, described with an object.
    all_available = 'all_available_example' # str | If set, the method returns a complete history of statuses/commands. (optional)
    since = 1699262836 # int | A Unix timestamp; if specified, the method returns all device commands inclusivelly newer than value of specified timestamp. (optional)

    try:
        api_response = api_instance.list_commands(company_name, car_name, sdevice_id, all_available=all_available, since=since)
        print("The response of DeviceApi->list_commands:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeviceApi->list_commands: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **company_name** | **str**| Name of the company, following a pattern &#39;^[0-9a-z_]+$&#39;. | 
 **car_name** | **str**| Name of the Car, following a pattern &#39;^[0-9a-z_]+$&#39;. | 
 **sdevice_id** | **str**| The Id of the Device, described with an object. | 
 **all_available** | **str**| If set, the method returns a complete history of statuses/commands. | [optional] 
 **since** | **int**| A Unix timestamp; if specified, the method returns all device commands inclusivelly newer than value of specified timestamp. | [optional] 

### Return type

[**List[Message]**](Message.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

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
> List[Message] list_statuses(company_name, car_name, sdevice_id, all_available=all_available, since=since)



It returns list of the Device Statuses.

### Example

* Api Key Authentication (ApiKeyAuth):
```python
import time
import os
import http_api_client
from http_api_client.models.message import Message
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiKeyAuth
configuration.api_key['ApiKeyAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiKeyAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    company_name = 'test_company' # str | Name of the company, following a pattern '^[0-9a-z_]+$'.
    car_name = 'test_car' # str | Name of the Car, following a pattern '^[0-9a-z_]+$'.
    sdevice_id = '47_2_test_device' # str | The Id of the Device, described with an object.
    all_available = 'all_available_example' # str | If set, the method returns a complete history of statuses/commands. (optional)
    since = 1699262836 # int | A Unix timestamp; if specified, the method returns all device statuses inclusivelly older than value of specified timestamp. (optional)

    try:
        api_response = api_instance.list_statuses(company_name, car_name, sdevice_id, all_available=all_available, since=since)
        print("The response of DeviceApi->list_statuses:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DeviceApi->list_statuses: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **company_name** | **str**| Name of the company, following a pattern &#39;^[0-9a-z_]+$&#39;. | 
 **car_name** | **str**| Name of the Car, following a pattern &#39;^[0-9a-z_]+$&#39;. | 
 **sdevice_id** | **str**| The Id of the Device, described with an object. | 
 **all_available** | **str**| If set, the method returns a complete history of statuses/commands. | [optional] 
 **since** | **int**| A Unix timestamp; if specified, the method returns all device statuses inclusivelly older than value of specified timestamp. | [optional] 

### Return type

[**List[Message]**](Message.md)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

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
> send_commands(company_name, car_name, sdevice_id, message=message)



It adds new device Commands.

### Example

* Api Key Authentication (ApiKeyAuth):
```python
import time
import os
import http_api_client
from http_api_client.models.message import Message
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiKeyAuth
configuration.api_key['ApiKeyAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiKeyAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    company_name = 'test_company' # str | Name of the company, following a pattern '^[0-9a-z_]+$'.
    car_name = 'test_car' # str | Name of the Car, following a pattern '^[0-9a-z_]+$'.
    sdevice_id = '47_2_test_device' # str | The Id of the Device, described with an object.
    message = [{"timestamp":1700139157,"device_id":{"module_id":47,"type":2,"role":"test_device","name":"Test Device"},"payload":{"payload_type":1,"encoding":1,"data":"U2F5IGhlbGxv"}}] # List[Message] | Commands to be executed by the device. (optional)

    try:
        api_instance.send_commands(company_name, car_name, sdevice_id, message=message)
    except Exception as e:
        print("Exception when calling DeviceApi->send_commands: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **company_name** | **str**| Name of the company, following a pattern &#39;^[0-9a-z_]+$&#39;. | 
 **car_name** | **str**| Name of the Car, following a pattern &#39;^[0-9a-z_]+$&#39;. | 
 **sdevice_id** | **str**| The Id of the Device, described with an object. | 
 **message** | [**List[Message]**](Message.md)| Commands to be executed by the device. | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

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
> send_statuses(company_name, car_name, sdevice_id, message=message)



Add statuses received from the Device.

### Example

* Api Key Authentication (ApiKeyAuth):
```python
import time
import os
import http_api_client
from http_api_client.models.message import Message
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: ApiKeyAuth
configuration.api_key['ApiKeyAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['ApiKeyAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.DeviceApi(api_client)
    company_name = 'test_company' # str | Name of the company, following a pattern '^[0-9a-z_]+$'.
    car_name = 'test_car' # str | Name of the Car, following a pattern '^[0-9a-z_]+$'.
    sdevice_id = '47_2_test_device' # str | The Id of the Device, described with an object.
    message = [{"timestamp":1700139157,"device_id":{"module_id":47,"type":2,"role":"test_device","name":"Test Device"},"payload":{"payload_type":0,"encoding":1,"data":"QnJpbmdBdXRv"}},{"timestamp":1700145485,"device_id":{"module_id":47,"type":2,"role":"test_device","name":"Test Device"},"payload":{"payload_type":0,"encoding":1,"data":"U3RhcnQgd29ya2luZw=="}},{"timestamp":1700145490,"device_id":{"module_id":47,"type":2,"role":"test_device","name":"Test Device"},"payload":{"payload_type":0,"encoding":0,"data":{"description":"Just keep working"}}}] # List[Message] | Statuses to be send by the device. (optional)

    try:
        api_instance.send_statuses(company_name, car_name, sdevice_id, message=message)
    except Exception as e:
        print("Exception when calling DeviceApi->send_statuses: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **company_name** | **str**| Name of the company, following a pattern &#39;^[0-9a-z_]+$&#39;. | 
 **car_name** | **str**| Name of the Car, following a pattern &#39;^[0-9a-z_]+$&#39;. | 
 **sdevice_id** | **str**| The Id of the Device, described with an object. | 
 **message** | [**List[Message]**](Message.md)| Statuses to be send by the device. | [optional] 

### Return type

void (empty response body)

### Authorization

[ApiKeyAuth](../README.md#ApiKeyAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The statuses have been sent. |  -  |
**500** | The statuses could not been sent due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


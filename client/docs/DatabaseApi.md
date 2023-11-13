# http_api_client.DatabaseApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**connect_to_database**](DatabaseApi.md#connect_to_database) | **PUT** / | 


# **connect_to_database**
> connect_to_database(connect_to_database_request=connect_to_database_request)



Connects to database

### Example

```python
import time
import os
import http_api_client
from http_api_client.models.connect_to_database_request import ConnectToDatabaseRequest
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
    api_instance = http_api_client.DatabaseApi(api_client)
    connect_to_database_request = http_api_client.ConnectToDatabaseRequest() # ConnectToDatabaseRequest | Login data (optional)

    try:
        api_instance.connect_to_database(connect_to_database_request=connect_to_database_request)
    except Exception as e:
        print("Exception when calling DatabaseApi->connect_to_database: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **connect_to_database_request** | [**ConnectToDatabaseRequest**](ConnectToDatabaseRequest.md)| Login data | [optional] 

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
**200** | Connection is estabilished |  -  |
**500** | Cannot connect due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


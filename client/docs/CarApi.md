# http_api_client.CarApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**available_cars**](CarApi.md#available_cars) | **GET** /cars | 


# **available_cars**
> List[str] available_cars()



Return list of available cars for all companies registered in the database.<br> Each item list has the format: '&lt;company name&gt;_&lt;car name&gt;'.

### Example

```python
import time
import os
import http_api_client
from http_api_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = http_api_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with http_api_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = http_api_client.CarApi(api_client)

    try:
        api_response = api_instance.available_cars()
        print("The response of CarApi->available_cars:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CarApi->available_cars: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

**List[str]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A list of available cars. |  -  |
**500** | Cannot display avaialble cars due to internal server error. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)


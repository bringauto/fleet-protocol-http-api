# http_api_client.CarApi

All URIs are relative to *http://localhost:8080*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cars_available**](CarApi.md#cars_available) | **GET** /cars | 


# **cars_available**
> List[Car] cars_available()



It returns the list of available Cars.

### Example

```python
import time
import os
import http_api_client
from http_api_client.models.car import Car
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
    api_instance = http_api_client.CarApi(api_client)

    try:
        api_response = api_instance.cars_available()
        print("The response of CarApi->cars_available:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CarApi->cars_available: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**List[Car]**](Car.md)

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


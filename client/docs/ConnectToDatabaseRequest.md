# ConnectToDatabaseRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dialect** | **str** |  | [optional] 
**dbapi** | **str** |  | [optional] 
**location** | **str** |  | [optional] 
**username** | **str** |  | [optional] 
**password** | **str** |  | [optional] 

## Example

```python
from http_api_client.models.connect_to_database_request import ConnectToDatabaseRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ConnectToDatabaseRequest from a JSON string
connect_to_database_request_instance = ConnectToDatabaseRequest.from_json(json)
# print the JSON string representation of the object
print ConnectToDatabaseRequest.to_json()

# convert the object into a dict
connect_to_database_request_dict = connect_to_database_request_instance.to_dict()
# create an instance of ConnectToDatabaseRequest from a dict
connect_to_database_request_form_dict = connect_to_database_request.from_dict(connect_to_database_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



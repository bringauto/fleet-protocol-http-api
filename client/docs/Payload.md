# Payload

A message passed to device (command) or by device (status).

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **int** |  | [optional] 
**encoding** | **int** |  | [optional] 
**data** | **object** |  | [optional] 

## Example

```python
from http_api_client.models.payload import Payload

# TODO update the JSON string below
json = "{}"
# create an instance of Payload from a JSON string
payload_instance = Payload.from_json(json)
# print the JSON string representation of the object
print Payload.to_json()

# convert the object into a dict
payload_dict = payload_instance.to_dict()
# create an instance of Payload from a dict
payload_form_dict = payload.from_dict(payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



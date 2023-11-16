# Payload

Payload of the message, containing message type (status or command), encoding and data.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **int** | Type of the payload, enumerated as follows: &lt;br&gt; 0 - STATUS &lt;br&gt; 1 - COMMAND | [optional] 
**encoding** | **int** | Encoding of the payload, enumerated as follows: &lt;br&gt; 0 - JSON &lt;br&gt; 1 - BASE64 | [optional] 
**data** | [**PayloadData**](PayloadData.md) |  | [optional] 

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



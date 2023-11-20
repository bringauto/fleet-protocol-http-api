# Module

A module containing at least one device (specified by device Id).

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**module_id** | **int** | Id (unsigned integer) of the module. | [optional] 
**device_list** | [**List[DeviceId]**](DeviceId.md) | List of Ids of devices contained in the module. | [optional] 

## Example

```python
from http_api_client.models.module import Module

# TODO update the JSON string below
json = "{}"
# create an instance of Module from a JSON string
module_instance = Module.from_json(json)
# print the JSON string representation of the object
print Module.to_json()

# convert the object into a dict
module_dict = module_instance.to_dict()
# create an instance of Module from a dict
module_form_dict = module.from_dict(module_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)



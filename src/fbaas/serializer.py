import json
from inspect import isclass


def serialize(data):
    """Serializes the data to JSON"""
    
    print(f'Serializing {data}')
    
    if isclass(data):
        as_dict = dict(data.__dict__)
        print(f'Class serialized as {as_dict}')
        return json.dumps(as_dict)
    
    return json.dumps(data)

def deserialize(data):
    """Deserializes the data from JSON"""
    return json.loads(data)

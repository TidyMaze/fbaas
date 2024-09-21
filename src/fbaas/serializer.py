import json
from inspect import isclass

def clean_for_dunder(data):
    """Cleans the data for dunder fields"""
    
    if isclass(data):
        as_dict = dict(data.__dict__)
        
        # filter out all fields starting with __ (recursive)
        cleaned_for_dunder = {k: clean_for_dunder(v) for k, v in as_dict.items() if not k.startswith('__')}
        
        return cleaned_for_dunder
    elif isinstance(data, dict):
        return {k: clean_for_dunder(v) for k, v in data.items() if not k.startswith('__')}
    elif isinstance(data, list):
        return [clean_for_dunder(v) for v in data]
    
    return data

def serialize(data):
    """Serializes the data to JSON"""
    
    print(f'Serializing {data}')
    
    if isclass(data):
        as_dict = dict(data.__dict__)
        print(f'Class serialized as {as_dict}')
        
        # filter out all fields starting with __ (recursive)
        cleaned_for_dunder = {k: v for k, v in as_dict.items() if not k.startswith('__')}
        
        print(f'Class serialized (after cleaning) as {cleaned_for_dunder}')
        
        return json.dumps(cleaned_for_dunder)
    
    return json.dumps(clean_for_dunder(data))

def deserialize(data):
    """Deserializes the data from JSON"""
    return json.loads(data)

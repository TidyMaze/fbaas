from inspect import isclass

endpoints = []

def add_watcher_to(stuff, path='root'):
    print(f'Watching {stuff} at path {path} that is a {type(stuff)}')
    
    if isinstance(stuff, dict):
        for attr in dir(stuff):
            if not attr.startswith('_'):
                print(f'Attribute {attr} is a {type(getattr(stuff, attr))}')
                child_path = f'{path}.{attr}'
                add_watcher_to(getattr(stuff, attr), child_path)
    elif isinstance(stuff, list):
        for i, item in enumerate(stuff):
            child_path = f'{path}[{i}]'
            add_watcher_to(item, child_path)
    elif isclass(stuff):
        print(f'Class {stuff.__name__}')
        for attr in dir(stuff):
            if not attr.startswith('_'):
                print(f'Attribute {attr} is a {type(getattr(stuff, attr))}')
                child_path = f'{path}.{attr}'
                add_watcher_to(getattr(stuff, attr), child_path)
    else:
        print(f'Unknown type {type(stuff)}')
    

# state decorator synchronises the state with the storage
def state():
    def decorator(cls):
        print(f'Registering state {cls.__name__}')
        add_watcher_to(cls)
    
        return cls
    return decorator

def get(param):
    def decorator(f):
        endpoints.append(('GET', param, f))
        return f
    return decorator

def post(param):
    def decorator(f):
        endpoints.append(('POST', param, f))
        return f
    return decorator

def delete(param):
    def decorator(f):
        endpoints.append(('DELETE', param, f))
        return f
    return decorator

from inspect import isclass, isbuiltin

from fbaas.observable_proxy import add_watcher_to

endpoints = []
    

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

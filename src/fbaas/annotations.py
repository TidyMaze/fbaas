from inspect import isclass, isbuiltin

from fbaas.observable_proxy import wrap, unwrap, Observer
from fbaas.storage import Storage

endpoints = []
    
class StateObserver(Observer):
    """This observer synchronises the state with the storage"""
    
    def __init__(self, global_state, storage):
        self.global_state = global_state
        self.storage = storage
        
    def notify(self, diff):
        print(f'Notifying state observer with diff {diff}')
        # not using diff for now, just updating the whole state
        self.storage.update(self.global_state)

# state decorator synchronises the state with the storage
def state():
    def decorator(cls):
        print(f'Registering state {cls.__name__}')
        
        storage = Storage.get_instance()
        
        obs = StateObserver(cls, storage)
    
        return wrap(cls, obs)
    
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

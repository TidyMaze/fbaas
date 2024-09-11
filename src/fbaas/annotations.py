endpoints = []

# state decorator synchronises the state with the storage
def state():
    def decorator(cls):
        print(f'Registering state {cls.__name__}')
    
        # redefine the __setattr__ method to synchronise the state with the storage
        def __setattr__(self, name, value):
            print(f'Updating state {name} with value {value}')
            super(cls, self).__setattr__(name, value)
            
            if isinstance(value, dict):
                print(f'Watching attribute {name}')
                setattr(self, name, __setattr__)
                
                for attr in dir(value):
                    if not attr.startswith('_'):
                        print(f'Attribute {attr} is a {type(getattr(value, attr))}')
                        if isinstance(getattr(value, attr), (list, dict)):
                            print(f'Watching attribute {attr}')
                            setattr(value, attr, __setattr__)
            else:
                print(f'Attribute {name} is a {type(value)}')
                    
            
        cls.__setattr__ = __setattr__
        
        # also define the __setattr__ method for all fields of the class itself (deep)
        for attr in dir(cls):
            if not attr.startswith('_') and isinstance(getattr(cls, attr), (list, dict)):
                print(f'Watching attribute {attr}')
                setattr(cls, attr, __setattr__)
        
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

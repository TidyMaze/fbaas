endpoints = []

# state decorator synchronises the state with the storage
def state():
    def decorator(cls):
        print(f'Registering state {cls.__name__}')
    
        # redefine the __setattr__ method to synchronise the state with the storage
        def __setattr__(self, name, value):
            print(f'Updating state {name} with value {value}')
            super(cls, self).__setattr__(name, value)
            
        cls.__setattr__ = __setattr__
        
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



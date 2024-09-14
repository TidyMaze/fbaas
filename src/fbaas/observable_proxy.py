from idlelib.configdialog import is_int

from deepdiff import DeepDiff

class ObservableDict:
    
    def __init__(self, wrapped, observer):
        self._observer: Observer = observer
        self._wrapped: dict = wrapped
    
    def __setitem__(self, key, value):
        self._wrapped[key] = wrap(value, self._observer)
        self._notify()

    def __getitem__(self, key):
        return self._wrapped[key]

    def _notify(self):
        print('Notifying changes')
        self._observer.notify(self)
        
    def __eq__(self, other):
        return self._wrapped == other
    
    def __str__(self):
        return f'ObservableDict({self._wrapped})'
    
    def __repr__(self):
        return f'ObservableDict({self._wrapped})'

class ObservableList:
    def __init__(self, wrapped, observer):
        self._observer = observer
        self._wrapped = wrapped
    
    def __setitem__(self, key, value):
        self._wrapped[key] = wrap(value)
        self._notify()

    def __getitem__(self, key):
        return self._wrapped[key]

    def _notify(self):
        print('Notifying changes')
        self._observer.notify(self)
        
    def __eq__(self, other):
        return self._wrapped == other

    def __str__(self):
        return f'ObservableList({self._wrapped})'
    
    def __repr__(self):
        return f'ObservableList({self._wrapped})'

def is_wrapped(state):
    return isinstance(state, ObservableDict) or isinstance(state, ObservableList)

def wrap(state, observer):
    if is_wrapped(state):
        return state
    
    if isinstance(state, dict):
        return ObservableDict(state, observer)
    elif isinstance(state, list):
        return ObservableList(state, observer)
    elif is_int(state):
        return state
    else:
        raise ValueError(f'Unsupported type {type(state)}')

class Observer:
    def notify(self, state):
        print(f'Changes detected: {state}')

def build_state():
    state = {
        'a': 1,
        'b': [{'c': 3, 'd': 4}],
        'e': {'f': 6}
    }
    
    observer = Observer()
    
    return wrap(state, observer)

def test_assign_root_scalar():
    state = build_state()
    state['a'] = 2
    assert state == {'a': 2, 'b': [{'c': 3, 'd': 4}], 'e': {'f': 6}}
    
def test_assign_root_list():
    state = build_state()
    state['b'] = [{'c': 3, 'd': 4}, {'c': 5, 'd': 6}]
    assert state == {'a': 1, 'b': [{'c': 3, 'd': 4}, {'c': 5, 'd': 6}], 'e': {'f': 6}}

def test_assign_root_dict():
    state = build_state()
    state['e'] = {'f': 7}
    assert state == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': 7}}
    
def test_assign_list_item_scalar():
    state = build_state()
    state['b'][0]['c'] = 5
    assert state == {'a': 1, 'b': [{'c': 5, 'd': 4}], 'e': {'f': 6}}
    
def test_assign_list_item_list():
    state = build_state()
    state['b'][0] = {'c': 5, 'd': 6}
    assert state == {'a': 1, 'b': [{'c': 5, 'd': 6}], 'e': {'f': 6}}
    
def test_assign_list_item_dict():
    state = build_state()
    state['b'][0] = {'c': 5}
    assert state == {'a': 1, 'b': [{'c': 5}], 'e': {'f': 6}}

def test_assign_dict_item_scalar():
    state = build_state()
    state['e']['f'] = 7
    assert state == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': 7}}
    
def test_assign_dict_item_list():
    state = build_state()
    state['e']['f'] = [7]
    assert state == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': [7]}}
    
def test_assign_dict_item_dict():
    state = build_state()
    state['e']['f'] = {'g': 7}
    assert state == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': {'g': 7}}}

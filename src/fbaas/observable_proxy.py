from abc import ABC, abstractmethod
from copy import deepcopy
from idlelib.configdialog import is_int

from deepdiff import DeepDiff


class ObservableDict:

    def __init__(self, wrapped, observer):
        self._observer: Observer = observer
        self._wrapped: dict = {k: wrap(v, observer) for k, v in wrapped.items()}

    def __setitem__(self, key, value):
        # Deep copy the state
        old_state = deepcopy(self._wrapped)
        self._wrapped[key] = wrap(value, self._observer)
        self._notify(old_state, unwrap(self._wrapped))

    def __getitem__(self, key):
        return self._wrapped[key]

    def _notify(self, old_state, new_state):
        print(f'Notifying changes: {old_state} -> {new_state}') 
        diff = DeepDiff(old_state, new_state)
        self._observer.notify(diff)

    def __eq__(self, other):
        return self._wrapped == other

    def __repr__(self):
        return f'ObservableDict({self._wrapped})'


class ObservableList:
    def __init__(self, wrapped, observer):
        self._observer = observer
        self._wrapped: list = [wrap(v, observer) for v in wrapped]

    def __setitem__(self, key, value):
        old_state = deepcopy(self._wrapped)
        self._wrapped[key] = wrap(value, self._observer)
        self._notify(old_state, unwrap(self._wrapped))

    def __getitem__(self, key):
        return self._wrapped[key]

    def _notify(self, old_state, new_state):
        print(f'Notifying changes: {old_state} -> {new_state}')
        diff = DeepDiff(old_state, new_state)
        self._observer.notify(diff)

    def __eq__(self, other):
        return self._wrapped == other

    def __repr__(self):
        return f'ObservableList({self._wrapped})'
    
def is_wrapped(state):
    return isinstance(state, ObservableDict) or isinstance(state, ObservableList)


def wrap(state, observer):
    if is_wrapped(state):
        print(f'State is already wrapped: {state}')
        return state

    if isinstance(state, dict):
        print(f'Wrapping state {state} in ObservableDict')
        return ObservableDict(state, observer)
    elif isinstance(state, list):
        print(f'Wrapping state {state} in ObservableList')
        return ObservableList(state, observer)
    elif is_int(state) or isinstance(state, str):
        print(f'Keeping state {state} as is (scalar)')
        return state
    else:
        raise ValueError(f'Unsupported type {type(state)}')

def unwrap(state):
    if isinstance(state, ObservableDict):
        inner = state._wrapped
        return {k: unwrap(v) for k, v in inner.items()}
    elif isinstance(state, ObservableList):
        inner = state._wrapped
        return [unwrap(v) for v in inner]
    elif isinstance(state, dict):
        return {k: unwrap(v) for k, v in state.items()}
    elif isinstance(state, list):
        return [unwrap(v) for v in state]
    else:
        return state

class Observer(ABC):
    @abstractmethod
    def notify(self, diff):
        print(f'Changes detected: {diff}')


class TestObserver(Observer):
    
    def __init__(self):
        self.notified_diff = None
    
    def notify(self, diff):
        print(f'Changes detected: {diff}')
        self.notified_diff = diff


def build_state() -> (ObservableDict, Observer):
    state: dict | list = {
        'a': 1,
        'b': [{'c': 3, 'd': 4}],
        'e': {'f': 6}
    }

    observer = TestObserver()

    return wrap(state, observer), observer


def test_assign_root_scalar():
    state, obs = build_state()
    state['a'] = 2
    assert state._wrapped == {'a': 2, 'b': [{'c': 3, 'd': 4}], 'e': {'f': 6}}
    assert obs.notified_diff == {'values_changed': {'root[\'a\']': {'new_value': 2, 'old_value': 1}}}

def test_assign_root_list():
    state, obs = build_state()
    state['b'] = [{'c': 3, 'd': 4}, {'c': 5, 'd': 6}]
    assert state._wrapped == {'a': 1, 'b': [{'c': 3, 'd': 4}, {'c': 5, 'd': 6}], 'e': {'f': 6}}
    assert obs.notified_diff == {'iterable_item_added': {"root['b'][1]": {'c': 5, 'd': 6}}}


def test_assign_root_dict():
    state, obs = build_state()
    state['e'] = {'f': 7}
    assert state._wrapped == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': 7}}
    assert obs.notified_diff == {'values_changed': {"root['e']['f']": {'new_value': 7, 'old_value': 6}}}


def test_assign_list_item_scalar():
    state, obs = build_state()
    state['b'][0]['c'] = 5
    assert state._wrapped == {'a': 1, 'b': [{'c': 5, 'd': 4}], 'e': {'f': 6}}
    assert obs.notified_diff == {'values_changed': {"root['b'][0]['c']": {'new_value': 5, 'old_value': 3}}}


def test_assign_list_item_list():
    state, obs = build_state()
    state['b'][0] = {'c': 5, 'd': 6}
    assert state._wrapped == {'a': 1, 'b': [{'c': 5, 'd': 6}], 'e': {'f': 6}}


def test_assign_list_item_dict():
    state, obs = build_state()
    state['b'][0] = {'c': 5}
    assert state._wrapped == {'a': 1, 'b': [{'c': 5}], 'e': {'f': 6}}


def test_assign_dict_item_scalar():
    state, obs = build_state()
    state['e']['f'] = 7
    assert state._wrapped == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': 7}}


def test_assign_dict_item_list():
    state, obs = build_state()
    state['e']['f'] = [7]
    assert state._wrapped == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': [7]}}


def test_assign_dict_item_dict():
    state, obs = build_state()
    state['e']['f'] = {'g': 7}
    assert state._wrapped == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': {'g': 7}}}

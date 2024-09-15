from abc import ABC, abstractmethod
from copy import deepcopy
from idlelib.configdialog import is_int

from deepdiff import DeepDiff


class ObservableDict:

    def __init__(self, wrapped, observer):
        self._observer: Observer = observer
        self._wrapped: dict = wrapped

    def __setitem__(self, key, value):
        # Deep copy the state
        old_state = deepcopy(self._wrapped)
        self._wrapped[key] = wrap(value, self._observer)
        self._notify(old_state, self._wrapped)

    def __getitem__(self, key):
        return self._wrapped[key]

    def _notify(self, old_state, new_state):
        print('Notifying changes')
        diff = DeepDiff(old_state, new_state)
        self._observer.notify(diff)

    def __eq__(self, other):
        return self._wrapped == other

    def __repr__(self):
        return f'ObservableDict({self._wrapped})'


class ObservableList:
    def __init__(self, wrapped, observer):
        self._observer = observer
        self._wrapped: list = wrapped

    def __setitem__(self, key, value):
        old_state = deepcopy(self._wrapped)
        self._wrapped[key] = wrap(value, self._observer)
        self._notify(old_state, self._wrapped)

    def __getitem__(self, key):
        return self._wrapped[key]

    def _notify(self, old_state, new_state):
        print('Notifying changes')
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
        return state

    if isinstance(state, dict):
        return ObservableDict(state, observer)
    elif isinstance(state, list):
        return ObservableList(state, observer)
    elif is_int(state):
        return state
    else:
        raise ValueError(f'Unsupported type {type(state)}')


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

def test_assign_root_list():
    state, obs = build_state()
    state['b'] = [{'c': 3, 'd': 4}, {'c': 5, 'd': 6}]
    assert state._wrapped == {'a': 1, 'b': [{'c': 3, 'd': 4}, {'c': 5, 'd': 6}], 'e': {'f': 6}}


def test_assign_root_dict():
    state, obs = build_state()
    state['e'] = {'f': 7}
    assert state._wrapped == {'a': 1, 'b': [{'c': 3, 'd': 4}], 'e': {'f': 7}}


def test_assign_list_item_scalar():
    state, obs = build_state()
    state['b'][0]['c'] = 5
    assert state._wrapped == {'a': 1, 'b': [{'c': 5, 'd': 4}], 'e': {'f': 6}}


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

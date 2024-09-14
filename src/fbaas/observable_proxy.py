from deepdiff import DeepDiff

class ObservableProxy:

    non_observable_fields = ['_observers', '_previous_state', '_obj']

    def __init__(self, obj):
        self.__dict__['_obj'] = self._wrap(obj)
        self.__dict__['_observers'] = []
        self.__dict__['_previous_state'] = self._obj.copy()

    def _wrap(self, value):
        """Recursively wrap dictionaries and lists in ObservableProxy."""
        if isinstance(value, dict):
            return {k: self._wrap(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._wrap(item) for item in value]
        else:
            return value

    def add_observer(self, observer):
        self._observers.append(observer)

    def notify(self, diff):
        for observer in self._observers:
            observer.update(diff)

    def _check_for_changes(self):
        """Check if there are any changes and notify observers."""
        diff = DeepDiff(self._previous_state, self._obj, ignore_order=True)
        if diff:
            self.notify(diff)
            self._previous_state = self._obj.copy()  # Update the previous state

    def __setattr__(self, key, value):
        """Intercept attribute setting."""
        
        if key in self.non_observable_fields:
            self.__dict__[key] = value
            return
        
        old_obj = self._obj
        self._obj[key] = self._wrap(value)
        self._check_for_changes()

    def __getitem__(self, key):
        """Intercept item getting."""
        return self._wrap(self._obj[key])

    def __setitem__(self, key, value):
        """Intercept item setting for lists and dictionaries."""
        old_obj = self._obj.copy()
        self._obj[key] = self._wrap(value)
        self._check_for_changes()

    def set_obj(self, new_obj):
        """Replace the whole object and notify observers."""
        self._obj = self._wrap(new_obj)
        self._check_for_changes()

class Observer:
    def update(self, diff):
        print("Detected change:", diff)

# Usage Example
data = {'a': 1, 'b': {'c': 3, 'd': [4, 5]}}
observable = ObservableProxy(data)
observer = Observer()

# Add observer
observable.add_observer(observer)

# Modify data at various levels
observable['a'] = 2  # Change at the root level
observable['b']['c'] = 4  # Change in nested dict
observable['b']['d'][1] = 6  # Change in nested list

# Replace the entire object
observable.set_obj({'a': 1, 'b': {'c': 3, 'd': [4, 7]}})

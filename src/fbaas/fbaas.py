import flask

from fbaas.annotations import endpoints
from fbaas.storage import Storage

# goal of this project is to create a backend as a service (similar to function as a service), with a state that is 
# automatically synchronised with a storage (database or nosql) every time the state changes in pytho code or in the storage.
# Architecture decisions:
# 1. The backend will be a REST API
# 2. The user can define a state in the code, annotated with the @state annotation
# 3. The user can define endpoints (functions), annotated with the HTTP method and the path
# 4. Annotations are used to define the state and the endpoints
# 5. The state will be automatically synchronised with the storage every time it changes
# 6. The storage will be a database or a nosql
# 7. The user doesn't need to write any code to synchronise the state with the storage
# 8. The user doesn't need to know the storage technology

def start():
    global all_methods
    app = flask.Flask(__name__)
    rules = {}
    # merge all functions with same path into the same url rule
    for (method, path, f) in endpoints:
        print(f'Registering endpoint {f.__name__} with path {path} and method {method}')

        # add the function to the list of rules
        if path not in rules:
            rules[path] = {}

        rules[path][method] = f

    def create_view_func(path, methods):
        def view_func():
            print(f'Calling view function for path {path}, known methods: {all_methods}')

            if flask.request.method == 'POST':
                return methods[flask.request.method](flask.request.json)
            elif flask.request.method == 'DELETE':
                return methods[flask.request.method](flask.request.view_args)
            else:
                return methods[flask.request.method]()

        view_func.__name__ = f'{path}_view_func'
        return view_func

    # then add the real rules to the Flask app
    for path, methods in rules.items():
        all_methods = methods.keys()

        print(f'Registering path {path} with methods {all_methods}. Functions: {methods}')

        app.add_url_rule(path, view_func=create_view_func(path, methods), methods=all_methods)
    storage = Storage()
    storage.init()
    app.run()

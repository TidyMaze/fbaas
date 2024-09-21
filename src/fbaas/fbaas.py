import flask

from fbaas.annotations import endpoints
from fbaas.storage import Storage

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

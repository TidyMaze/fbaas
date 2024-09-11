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
import flask.app

import fbaas.annotations

# Exemple of usage:

@fbaas.annotations.state()
class State:
    users = [
        {"name": "Alice"},
        {"name": "Bob"}
    ]


my_state = State()

@fbaas.annotations.get("/users")
def get_users():
    return my_state.users


@fbaas.annotations.post("/users")
def create_user(user):
    my_state.users.append(user)
    return my_state.users


# decorators add the function to the endpoints list
# the endpoints list is used to create the routes in the Flask

# create the routes in the Flask
app = flask.Flask(__name__)

rules = {}

# merge all functions with same path into the same url rule
for (method, path, f) in fbaas.annotations.endpoints:
    print(f'Registering endpoint {f.__name__} with path {path} and method {method}')
    
    # add the function to the list of rules
    if path not in rules:
        rules[path] = {}
        
    rules[path][method] = f
    
# then add the real rules to the Flask app
for path, methods in rules.items():
    all_methods = methods.keys()
    
    def view_func():
        if flask.request.method == 'POST':
            return methods[flask.request.method](flask.request.json)
        else:
            return methods[flask.request.method]()
    
    app.add_url_rule(path, view_func=view_func, methods=all_methods)

app.run()

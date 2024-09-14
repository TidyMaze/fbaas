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
import psycopg2

import fbaas.annotations

# Exemple of usage:

@fbaas.annotations.state()
class State:
    users = [
        {"name": "Alice"},
        {"name": "Bob"}
    ]
    banned_user = {"name": "Charlie"}


my_state = State()
my_state.lol = 1
my_state.another = { "a": 1, "b": 2 }
my_state.banned_user['name'] = "Charlie"


@fbaas.annotations.get("/users")
def get_users():
    return my_state.users


@fbaas.annotations.post("/users")
def create_user(user):
    my_state.users.append(user)
    return my_state.users

@fbaas.annotations.delete("/user/<name>")
def delete_user(name):
    my_state.users = [user for user in my_state.users if user["name"] != name]
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

def create_database():
    """Creates the main table: state using the library of choice, psycopg2"""
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"
    
    query_table = """
    CREATE TABLE state (
        id SERIAL PRIMARY KEY,
        data JSONB
    );
    """
    with psycopg2.connect(DATABASE_URL) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(query_table)
            
    
    

def initialize_storage():
    """Initializes the storage (database): creates the tables, etc."""
    create_database()

initialize_storage()

app.run()

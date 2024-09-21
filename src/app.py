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

import fbaas.annotations
from fbaas.fbaas import start
from fbaas.observable_proxy import unwrap

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

print(f'Initial state: {my_state.__dict__}')


@fbaas.annotations.get("/users")
def get_users():
    return unwrap(my_state.users)


@fbaas.annotations.post("/users")
def create_user(user):
    my_state.users.append(user)
    return unwrap(my_state.users)

@fbaas.annotations.delete("/user/<name>")
def delete_user(name):
    my_state.users = [user for user in my_state.users if user["name"] != name]
    return unwrap(my_state.users)

start()

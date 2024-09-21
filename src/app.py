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

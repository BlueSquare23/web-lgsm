"""
Looks at everything in the container. If it looks like a use case, auto-create
a function for it in this module. Used for shortening long container usecase
calls like this:

    servers = container.list_user_game_servers().execute(current_user.id)

To shorter more readable calls like this:

    servers = list_user_game_servers(current_user.id)
"""

from app.container import container

def _make_usecase(name):
    """
    Interface layer usecase factory. Creates functions for usecases defined in
    the container. 
    """
    def fn(*args, **kwargs):
        instance = getattr(container, name)()

        if not hasattr(instance, "execute"):
            raise TypeError(f"{name} is not a use case (missing .execute())")

        return instance.execute(*args, **kwargs)

    fn.__name__ = name
    fn.__qualname__ = name
    fn.__doc__ = f"Auto-generated wrapper for container.{name}().execute()"

    return fn


for attr in dir(container):
    if attr.startswith("_"):
        continue

    factory = getattr(container, attr)

    if not callable(factory):
        continue

    try:
        instance = factory()
    except TypeError:
        continue

    if hasattr(instance, "execute"):
        globals()[attr] = _make_usecase(attr)


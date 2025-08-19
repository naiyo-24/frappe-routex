from collections.abc import Callable


def get_base_package_name(func: Callable) -> str:
    return format_route(func.__module__.split(".")[0])


def load_module_for_app(app_name):
    import importlib
    import os
    import pkgutil

    from frappe import DoesNotExistError

    """
    Recursively searches for a function in any module inside the given app.

    :param app_name: The root package name (e.g., "frappe")
    :return: The function object if found, else None
    """

    try:
        package = importlib.import_module(app_name)
    except ModuleNotFoundError:
        raise DoesNotExistError

    package = importlib.import_module(app_name)
    package_path = os.path.dirname(package.__file__)

    for _, module_name, _ in pkgutil.walk_packages(
        [package_path], prefix=f"{app_name}."
    ):
        importlib.import_module(module_name)


def format_route(route: str, prefix_slash: bool = False) -> str:
    if prefix_slash and not route.startswith("/"):
        route = "/" + route
    return route.replace("_", "-")


def parse_route(route: str) -> str:
    return route.replace("-", "_")

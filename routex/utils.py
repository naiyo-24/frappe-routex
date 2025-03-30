from collections.abc import Callable


def get_base_package_name(func: Callable) -> str:
    return func.__module__.split(".")[0]

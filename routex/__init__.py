import frappe

from routex.api import handle
from routex.utils import get_base_package_name, format_route

__version__ = "0.0.1"
__title__ = "RouteX"

routex_whitelisted = {}


def routex_whitelist(
    route: str,
    group: str | None = None,
    allow_guest: bool = False,
    xss_safe: bool = False,
    methods: list = ["GET", "POST"],
):
    """
    Decorator to add REST API like route names to frappe's whitelist methods.
    This allows you to call the function using a URL like /api/<app_name>/<route>.
    Args:
        route (str): The route to whitelist the function for. Will be formatted as /api/<app_name>/<route>
        group (str | None, optional): The group to whitelist the function for. Creates path like /api/<app_name>/<group>/<route>. Defaults to None.
        allow_guest (bool, optional): Whether to allow guest access to the function. Defaults to False.
        xss_safe (bool, optional): Whether to make the function XSS safe. Defaults to False.
        methods (list, optional): The HTTP methods to allow for the function. Defaults to ["GET", "POST"].

    Returns:
        callable: The decorated function with whitelist and routing capabilities added.

    Example:
        @routex_whitelist("users", group="v1", methods=["GET"])
        def get_users():
            # This function will be accessible at /api/myapp/v1/users
            return {"users": [...]}
    """
    if not methods:
        methods = ["GET", "POST", "PUT", "DELETE"]

    def innerfn(fn: callable):
        from frappe.utils.typing_validations import validate_argument_types

        global routex_whitelisted

        in_request_or_test = (  # noqa: E731
            lambda: getattr(frappe.local, "request", None) or frappe.local.flags.in_test  # noqa: E731
        )

        if hasattr(fn, "__func__"):
            method = validate_argument_types(fn, apply_condition=in_request_or_test)
            fn = method.__func__
        else:
            fn = validate_argument_types(fn, apply_condition=in_request_or_test)

        app_name = get_base_package_name(fn)
        method = None

        method_path = app_name
        if group:
            method_path += format_route(group, prefix_slash=True)

        method_path += format_route(route, prefix_slash=True)

        routex_whitelisted[method_path] = f"{fn.__module__}.{fn.__name__}"

        fn = frappe.whitelist(
            allow_guest=allow_guest, xss_safe=xss_safe, methods=methods
        )(fn)
        return method or fn

    return innerfn


@routex_whitelist("/foo")
def foo():
    return "bar"


frappe.api.handle = handle

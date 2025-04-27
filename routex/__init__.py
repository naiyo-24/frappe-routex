import frappe

from routex.api import handle
from routex.utils import get_base_package_name

__version__ = "0.0.1"
__title__ = "routeX"

routex_whitelisted = {}


def routex_whitelist(
    route: str,
    group: str | None = None,
    allow_guest: bool = False,
    xss_safe: bool = False,
    methods: list = ["GET", "POST"],
):
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
            method_path += group

        method_path += route

        routex_whitelisted[method_path] = f"{fn.__module__}.{fn.__name__}"

        fn = frappe.whitelist(
            allow_guest=allow_guest, xss_safe=xss_safe, methods=methods
        )(fn)
        return method or fn

    return innerfn


@routex_whitelist("/foo/test")
def foo():
    return "bar"


frappe.api.handle = handle

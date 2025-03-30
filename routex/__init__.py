from routex.utils import get_base_package_name
import frappe
from routex.api import handle

__version__ = "0.0.1"
__title__ = "routeX"

routex_whitelisted = {}


def routex_whitelist(
    api_name: str,
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

        in_request_or_test = (
            lambda: getattr(frappe.local, "request", None) or frappe.local.flags.in_test
        )  # noqa: E731

        if hasattr(fn, "__func__"):
            method = validate_argument_types(fn, apply_condition=in_request_or_test)
            fn = method.__func__
        else:
            fn = validate_argument_types(fn, apply_condition=in_request_or_test)

        app_name = get_base_package_name(fn)
        sub_group = group
        method = None

        if not sub_group:
            sub_group = "base"

        app_apis = routex_whitelisted.get(app_name, {})

        if not app_apis:
            app_apis["app"] = app_name
            app_apis["apis"] = {"base": {}}

        if sub_group not in app_apis["apis"]:
            app_apis["apis"][sub_group] = {}

        if sub_group in app_apis["apis"]:
            app_apis["apis"][sub_group][api_name] = {}

        app_apis["apis"][sub_group][api_name] = frappe._dict(
            {
                "method": f"{fn.__module__}.{fn.__name__}",
                "allowed_http_method": methods,
                "allow_guest": allow_guest,
                "xss_safe": xss_safe,
            }
        )

        routex_whitelisted[app_name] = app_apis
        return method or fn

    return innerfn


# Monkey patch
from frappe import api

api.handle = handle

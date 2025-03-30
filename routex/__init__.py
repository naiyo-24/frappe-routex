from routex.utils import get_base_package_name
import frappe
from routex.api import handle

__version__ = "0.0.1"
__title__ = "routeX"

routex_whitelisted = {}
routex_guest_methods = []
routex_xss_safe_methods = []
routex_allowed_http_methods_for_whitelisted_func = {}
allowed_methods = ["GET", "POST", "PUT", "DELETE"]


def routex_whitelist(
    api_name: str,
    group: str | None = None,
    allow_guest: bool = False,
    xss_safe: bool = False,
    methods: list = ["GET", "POST"],
):
    if not methods:
        methods = ["GET", "POST", "PUT", "DELETE"]

    def innerfn(fn):
        from frappe.utils.typing_validations import validate_argument_types

        global routex_whitelisted, routex_guest_methods, routex_xss_safe_methods, routex_allowed_http_methods_for_whitelisted_func

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
            app_apis["apis"][sub_group][api_name] = fn

        routex_whitelisted[app_name] = app_apis

        api_path = f"/{app_name}/{sub_group}/{api_name}"
        routex_allowed_http_methods_for_whitelisted_func[api_path] = methods

        if allow_guest:
            routex_guest_methods.append(api_path)

            if xss_safe:
                routex_xss_safe_methods.add(api_path)
        return method or fn

    return innerfn


# Monkey patch
from frappe import api

api.handle = handle

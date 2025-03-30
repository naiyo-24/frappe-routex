from routex.utils import get_route_from_app_name
import frappe
from routex.api import handle

__version__ = "0.0.1"
__title__ = "Frappei"

frappei_whitelisted = {}
frappei_guest_methods = []
frappei_xss_safe_methods = []
frappei_allowed_http_methods_for_whitelisted_func = {}
allowed_methods = ["GET", "POST", "PUT", "DELETE"]



def frappei_whitelist(
    app_name: str,
    api_name: str,
    group: str | None = None,
    allow_guest: bool = False,
    xss_safe: bool = False,
    methods: list = ["GET", "POST"],
):
    def innerfn(fn):
        from frappe.utils.typing_validations import validate_argument_types

        global frappei_whitelisted, frappei_guest_methods, frappei_xss_safe_methods, frappei_allowed_http_methods_for_whitelisted_func

        app_route = get_route_from_app_name(app_name)
        sub_group = group
        method = None
        in_request_or_test = (
            lambda: getattr(frappe.local, "request", None) or frappe.local.flags.in_test
        )  # noqa: E731

        if hasattr(fn, "__func__"):
            method = validate_argument_types(fn, apply_condition=in_request_or_test)
            fn = method.__func__
        else:
            fn = validate_argument_types(fn, apply_condition=in_request_or_test)

        if not sub_group:
            sub_group = "base"

        app_apis = frappei_whitelisted.get(app_route, {})

        if not app_apis:
            app_apis["app"] = app_name
            app_apis["apis"] = {"base": {}}

        if sub_group not in app_apis["apis"]:	
            app_apis["apis"][sub_group] = {}
        if sub_group in app_apis["apis"]:
            app_apis["apis"][sub_group][api_name] = fn

        frappei_whitelisted[app_route] = app_apis

        api_path = f"/{app_route}/{sub_group}/{api_name}"
        frappei_allowed_http_methods_for_whitelisted_func[api_path] = methods

        if allow_guest:
            frappei_guest_methods.append(api_path)
        return method or fn

    return innerfn


# Monkey patch
from frappe import api

api.handle = handle

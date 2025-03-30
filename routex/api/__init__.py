from werkzeug.routing import Rule, Submount, Map
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
from frappe.exceptions import DoesNotExistError
import frappe
import routex
from frappe.handler import build_response
from frappe.api import API_URL_MAP
from routex.utils import load_module_for_app, is_valid_http_method, is_whitelisted


def handle_api_call(route: str):

    route = route.split("/")
    route_length = len(route)
    if route_length < 2 or route_length > 3:
        raise DoesNotExistError

    sub_group = "base"
    if route_length == 3:
        app_name, sub_group, api_name = route

    if route_length == 2:
        app_name, api_name = route

    load_module_for_app(app_name)

    try:
        api = routex.routex_whitelisted[app_name]["apis"][sub_group][api_name]
        is_valid_http_method(api)
        is_whitelisted(api)
        return frappe.call(api.method, **frappe.form_dict)
    except:
        raise DoesNotExistError


url_rules = [
    Rule("/<path:route>", endpoint=handle_api_call),
]
URL_MAP = Map([Submount("/api", url_rules)], strict_slashes=False, merge_slashes=False)


def handle(request: Request):
    try:
        endpoint, arguments = API_URL_MAP.bind_to_environ(request.environ).match()
        data = endpoint(**arguments)
        if isinstance(data, Response):
            return data

        if data is not None:
            frappe.response["data"] = data
        return build_response("json")
    except NotFound:
        try:
            endpoint, arguments = URL_MAP.bind_to_environ(request.environ).match()
        except NotFound:
            raise DoesNotExistError
        data = endpoint(**arguments)
        if isinstance(data, Response):
            return data

        if data is not None:
            frappe.response["message"] = data
        return build_response("json")

import frappe
from frappe.api import API_URL_MAP
from frappe.exceptions import DoesNotExistError
from frappe.handler import build_response
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map, Rule, Submount
from werkzeug.wrappers import Request, Response

import routex
from routex.utils import is_valid_http_method, is_whitelisted, load_module_for_app


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
    except DoesNotExistError:
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

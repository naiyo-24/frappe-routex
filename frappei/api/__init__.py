from werkzeug.routing import Rule, Submount, Map
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
from frappe.exceptions import DoesNotExistError
import frappei
import frappe
from frappe.handler import build_response
from frappe.api import API_URL_MAP


def handle_api_call(route: str):
    # try:
    route = route.split("/")
    if len(route) == 2:
        app_route, api_name = route
        method = frappei.frappei_whitelisted[app_route]["apis"]["base"][api_name]
        return frappe.call(method, **frappe.form_dict)
    if len(route) == 3:
        app_route, sub_group, api_name = route
        method = frappei.frappei_whitelisted[app_route]["apis"][sub_group][api_name]
        return frappe.call(method, **frappe.form_dict)
    # except Exception:
    #     raise DoesNotExistError


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

import frappe
from frappe.api import handle as _handle
from frappe.exceptions import DoesNotExistError
from frappe.handler import build_response
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map, Rule, Submount
from werkzeug.wrappers import Request, Response

import routex
from routex.utils import load_module_for_app, parse_route


def handle_api_call(route: str):
    app_name = route.split("/")[0]
    if route not in routex.routex_whitelisted:
        load_module_for_app(parse_route(app_name))
    try:
        method = routex.routex_whitelisted.get(route, None)
        if not method:
            raise DoesNotExistError
        return frappe.handler.execute_cmd(method)
    except DoesNotExistError:
        raise DoesNotExistError


def handle(request: Request):
    try:
        return _handle(request)
    except (NotFound, DoesNotExistError):
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


url_rules = [
    Rule("/<path:route>", endpoint=handle_api_call),
]
URL_MAP = Map([Submount("/api", url_rules)], strict_slashes=False, merge_slashes=False)

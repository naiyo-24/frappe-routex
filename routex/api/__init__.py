from werkzeug.routing import Rule, Submount, Map
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
from frappe.exceptions import DoesNotExistError
import frappe
import routex
from frappe.handler import build_response
from frappe.api import API_URL_MAP
import importlib
import pkgutil
import os


def handle_api_call(route: str):

    route = route.split("/")

    if len(route) == 2:
        find_function_in_app(route[0])
        app_route, api_name = route
        method = routex.frappei_whitelisted[app_route]["apis"]["base"][api_name]
        return frappe.call(method, **frappe.form_dict)

    if len(route) == 3:
        find_function_in_app(route[0])
        app_route, sub_group, api_name = route
        method = routex.frappei_whitelisted[app_route]["apis"][sub_group][api_name]
        return frappe.call(method, **frappe.form_dict)


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


def find_function_in_app(app_name):
    """
    Recursively searches for a function in any module inside the given app.

    :param app_name: The root package name (e.g., "frappe")
    :param function_name: The function name to search for
    :return: The function object if found, else None
    """

    try:
        package = importlib.import_module(app_name)
    except ModuleNotFoundError:
        raise DoesNotExistError

    package = importlib.import_module(app_name)
    package_path = os.path.dirname(package.__file__)

    for _, module_name, _ in pkgutil.walk_packages(
        [package_path], prefix=f"{app_name}."
    ):
        try:
            module = importlib.import_module(module_name)
        except:
            pass

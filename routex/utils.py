from collections.abc import Callable


def get_base_package_name(func: Callable) -> str:
    return func.__module__.split(".")[0]


def load_module_for_app(app_name):
    import importlib
    from frappe import DoesNotExistError
    import os
    import pkgutil

    """
    Recursively searches for a function in any module inside the given app.

    :param app_name: The root package name (e.g., "frappe")
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

        importlib.import_module(module_name)


def is_valid_http_method(api):
    import frappe

    if frappe.flags.in_safe_exec:
        return

    http_method = frappe.local.request.method

    if http_method not in api.allowed_http_method:
        frappe.throw_permission_error()


def is_whitelisted(api):
    from frappe.utils import sanitize_html
    import frappe
    from frappe.utils import bold

    is_guest = frappe.session.user == "Guest"
    if is_guest and not api.allow_guest:
        summary = frappe._("You are not permitted to access this resource.")
        detail = frappe._("Function {0} is not whitelisted.").format(
            bold(f"{api.method}")
        )
        msg = f"<details><summary>{summary}</summary>{detail}</details>"
        frappe.throw(msg, PermissionError, title=frappe._("Method Not Allowed"))

    if is_guest and not api.xss_safe:
        # strictly sanitize form_dict
        # escapes html characters like <> except for predefined tags like a, b, ul etc.
        for key, value in frappe.form_dict.items():
            if isinstance(value, str):
                frappe.form_dict[key] = sanitize_html(value)

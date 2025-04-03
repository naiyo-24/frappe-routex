<div align="center">

# 🚀 RouteX

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL3.0](https://img.shields.io/badge/license-AGPL--v3-blue)](https://opensource.org/license/agpl-v3)

### Rest API compatible routes for Frappe

_RouteX is a Frappe app that enhances API routing by introducing RESTful endpoints alongside Frappe’s default dotted path approach. It provides a more intuitive and flexible way to define and manage API routes in Frappe applications._

[Quick Start](#quick-start) • [Examples](#-examples) • [Support](#-support)

</div>

## ✨ Features

<table style="border: none;" cellspacing="20" cellpadding="10">
<tr style="border: none;">
<td style="border: none; vertical-align: top; width: 33%;">
<h3>RestAPI compatible</h3>

- Fully supports RESTful principles, making it easy to integrate with external services.

- Supports slashed path-based routing (e.g., /api/app-name/<route-name>) instead of Frappe’s dotted path convention for cleaner and more intuitive URLs.

</td>
<td style="border: none; vertical-align: top; width: 33%;">
<h3>Grouped Routes</h3>

- Organize multiple related API endpoints under a single namespace.
- Helps maintain cleaner, more structured API management.
</td>
<td style="border: none; vertical-align: top; width: 33%;">
<h3>Custom route names</h3>

- Allows defining human-readable and meaningful route names.
- Enhances debugging and logging by providing easily identifiable route identifiers.
</td>
</tr>
</tr>
</table>

## 🛠️ Requirements

- Python 3.11 or higher
- Frappe

## 🚀 Quick Start

```bash
# Install RouteX
bench get-app https://github.com/niraj2477/routex
bench install-app routex
```

## 📚 Examples

### Usage

```python
# Use routex_whitelist function to add your route, In this example we are are defineing a route name "ding" that will be accessible via /api/[app-name]/ding
@routex_whitelist("ding")
def ding():
    return "dong"

```

```python
# use routex_whitelist function to add your group name and route name, In this example we are defining a group name "ping" and route name "pong" that will be accessible via /api/[app-name]/ping/pong
@routex_whitelist("ping", "pong")
def ping():
    return "dong"
```

## 🤝 Support

- 🐛 [Report issues](https://github.com/niraj2477/routex/issues)
- 💬 [Discussions](https://github.com/niraj2477/routex/discussions)
- 🌟 Star us on GitHub!

## 👏 authors

[@elifvish](https://github.com/elifvish)
[@niraj2477](https://gihub.com/niraj2477)
[@dhsathiya](https://github.com/dhsathiya)

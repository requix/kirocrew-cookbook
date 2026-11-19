"""Interactive widgets, one module per widget.

A page embeds a widget with an empty fence:

    ```widget fence-check
    ```

Each widget is three things, all named after the widget:

- ``content/widgets/<name>.yaml``  the data: labels, cases, steps. Edit freely, then rebuild.
- ``build/preview/widgets/<name>.py``  ``load(project) -> dict`` reads and checks the YAML
  (raise ``WidgetError`` with a clear message), ``markdown(data) -> str`` gives the plain
  version for the .md copy of the page and for llms.txt.
- ``build/preview/assets/widgets/<name>.js`` and ``.css``  the browser side. The JS finds
  ``[data-widget="<name>"]`` and reads its data from the ``script[data-widget-data]`` inside.

The build fails if a fence names a widget that does not exist, or if ``load`` raises.
"""
from __future__ import annotations

import html
import importlib
import json
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "widgets"
FENCE = re.compile(r"```widget ([a-z0-9-]+)\n```\n?")
NAME = re.compile(r"^[a-z0-9-]+$")


class WidgetError(Exception):
    pass


def _module(name: str):
    if not NAME.match(name):
        raise WidgetError(f"bad widget name '{name}'")
    try:
        mod = importlib.import_module(f"widgets.{name.replace('-', '_')}")
    except ModuleNotFoundError as exc:
        raise WidgetError(f"no widget '{name}' (expected build/preview/widgets/{name.replace('-', '_')}.py)") from exc
    for f in ("js", "css"):
        if not (ASSETS / f"{name}.{f}").exists():
            raise WidgetError(f"widget '{name}' has no assets/widgets/{name}.{f}")
    return mod


def load(name: str, project: Path) -> dict:
    return _module(name).load(project)


def html_for(name: str, project: Path, rel: str) -> str:
    """The widget's mount point, its data and its assets. ``rel`` is the path back to the site root."""
    data = load(name, project)
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(data.get("title", ""))
    return (f'<div class="kw kw-{name}" data-widget="{name}" role="group" aria-label="{title}">'
            f'<script type="application/json" data-widget-data>{payload}</script>'
            f'<noscript><p>This interactive needs JavaScript. The page text above covers the same ground.</p></noscript>'
            f'</div>\n'
            f'<link rel="stylesheet" href="{rel}assets/widgets/widget-base.css">\n'
            f'<link rel="stylesheet" href="{rel}assets/widgets/{name}.css">\n'
            f'<script type="module" src="{rel}assets/widgets/{name}.js"></script>\n')


def markdown_for(name: str, project: Path) -> str:
    return _module(name).markdown(load(name, project)).rstrip() + "\n\n"


FORBIDDEN_TEXT = ("·", "→", "->")


def check_text(name: str, node) -> None:
    """Reject typographic tells (middle dots, arrows) anywhere in a widget's visible text."""
    if isinstance(node, str):
        for bad in FORBIDDEN_TEXT:
            if bad in node:
                raise WidgetError(f"{name}.yaml: visible text must not contain '{bad}': {node!r}")
    elif isinstance(node, dict):
        for v in node.values():
            check_text(name, v)
    elif isinstance(node, list):
        for v in node:
            check_text(name, v)


def read_yaml(project: Path, name: str) -> dict:
    import yaml
    path = Path(project) / "content" / "widgets" / f"{name}.yaml"
    try:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WidgetError(f"{name}.yaml: cannot read: {exc}") from exc
    if not isinstance(spec, dict):
        raise WidgetError(f"{name}.yaml: must be a mapping")
    return spec

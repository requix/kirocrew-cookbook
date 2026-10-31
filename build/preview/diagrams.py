"""Small diagrams written as data and drawn with HTML and CSS at build time.

Drawings made of box characters break as soon as a font lacks one glyph (the
cookbook's code font has none of them), and a screen reader reads them as noise.
These two fences replace them. Both render to plain lists, so the text stays
selectable, wraps on a phone and reads in order without CSS.

```flow
- box: You
- box: KiroCrew gateway
  note: One process on your machine.
  via: label on the arrow into this box
- split:                      # boxes side by side; each branch is its own little flow
    - - box: Model
    - - box: Tools
```

Box keys: box (name), note, via, steps (numbered list inside), items (bullets inside),
accent (true marks the box the diagram is about). Text takes inline Markdown.
A mapping with `flow:` and `caption:` adds a caption under the diagram.

```tree
~/apps/standup-notes/
  app.json
  assets/
    icon.png  # a note after two spaces and a hash
```
"""
from __future__ import annotations

import html
import re
from typing import Callable

import yaml

esc = html.escape
BOX_KEYS = {"box", "note", "via", "steps", "items", "accent"}
SPLIT_KEYS = {"split", "via"}


class DiagramError(Exception):
    pass


# ---------------------------------------------------------------- flow
def _load_flow(src: str) -> tuple[list, str | None]:
    try:
        data = yaml.safe_load(src)
    except yaml.YAMLError as exc:
        raise DiagramError(f"flow: not valid YAML: {exc}") from None
    caption = None
    if isinstance(data, dict):
        extra = set(data) - {"flow", "caption"}
        if extra:
            raise DiagramError(f"flow: unknown key(s) {sorted(extra)}; use flow and caption")
        caption, data = data.get("caption"), data.get("flow")
    if not isinstance(data, list) or not data:
        raise DiagramError("flow: expected a list of boxes")
    _check_seq(data, "flow")
    return data, caption


def _check_seq(seq: list, where: str) -> None:
    for i, item in enumerate(seq):
        at = f"{where}[{i}]"
        if not isinstance(item, dict):
            raise DiagramError(f"{at}: expected a mapping with box or split")
        if "split" in item:
            extra = set(item) - SPLIT_KEYS
            branches = item["split"]
            if extra:
                raise DiagramError(f"{at}: unknown key(s) {sorted(extra)} on a split")
            if not isinstance(branches, list) or len(branches) < 2:
                raise DiagramError(f"{at}: a split needs at least two branches")
            for j, br in enumerate(branches):
                if not isinstance(br, list) or not br:
                    raise DiagramError(f"{at}.split[{j}]: a branch is a list of boxes")
                _check_seq(br, f"{at}.split[{j}]")
        elif "box" in item:
            extra = set(item) - BOX_KEYS
            if extra:
                raise DiagramError(f"{at}: unknown key(s) {sorted(extra)}; a box takes {sorted(BOX_KEYS)}")
            for key in ("steps", "items"):
                if key in item and (not isinstance(item[key], list) or not item[key]):
                    raise DiagramError(f"{at}: {key} must be a non-empty list")
        else:
            raise DiagramError(f"{at}: needs box or split")
        if i == 0 and item.get("via") and where == "flow":
            raise DiagramError(f"{at}: the first box has no arrow into it, so it takes no via")


def flow_html(src: str, inline: Callable[[str], str]) -> str:
    seq, caption = _load_flow(src)
    cap = f'<figcaption class="vc-flow__caption">{inline(str(caption))}</figcaption>' if caption else ""
    return f'<figure class="vc-flow">{_seq_html(seq, inline, top=True)}{cap}</figure>\n'


def _seq_html(seq: list, inline: Callable[[str], str], top: bool) -> str:
    out = []
    for i, item in enumerate(seq):
        via = item.get("via")
        if i == 0 and not top:
            # The first box of a branch: its label names the branch, no arrow.
            head = f'<p class="vc-flow__tag">{inline(str(via))}</p>' if via else ""
        elif i == 0:
            head = ""
        else:
            label = f"<span>{inline(str(via))}</span>" if via else ""
            head = f'<p class="vc-flow__via">{label}</p>'
        if "split" in item:
            branches = "".join(f'<li class="vc-flow__branch">{_seq_html(br, inline, top=False)}</li>'
                               for br in item["split"])
            body = f'<ul class="vc-flow__split">{branches}</ul>'
        else:
            body = _box_html(item, inline)
        out.append(f'<li class="vc-flow__step">{head}{body}</li>')
    return f'<ol class="vc-flow__seq">{"".join(out)}</ol>'


def _box_html(item: dict, inline: Callable[[str], str]) -> str:
    parts = [f'<p class="vc-flow__name">{inline(str(item["box"]))}</p>']
    if item.get("note"):
        parts.append(f'<p class="vc-flow__note">{inline(str(item["note"]))}</p>')
    if item.get("steps"):
        parts.append('<ol class="vc-flow__steps">' + "".join(f"<li>{inline(str(s))}</li>" for s in item["steps"]) + "</ol>")
    if item.get("items"):
        parts.append('<ul class="vc-flow__items">' + "".join(f"<li>{inline(str(s))}</li>" for s in item["items"]) + "</ul>")
    cls = "vc-flow__box vc-flow__box--accent" if item.get("accent") else "vc-flow__box"
    return f'<div class="{cls}">{"".join(parts)}</div>'


def flow_markdown(src: str) -> str:
    """The same flow as a numbered list, for the .md copy of a page."""
    seq, caption = _load_flow(src)
    lines = []
    for n, item in enumerate(seq, 1):
        via = f"_{item['via']}_ → " if item.get("via") else ""
        if "split" in item:
            lines.append(f"{n}. {via}Then:")
            for br in item["split"]:
                lines.append("   - " + " → ".join(_box_md(b, "tag" if k == 0 else "arrow") for k, b in enumerate(br)))
        else:
            lines.append(f"{n}. {via}{_box_md(item, 'none')}")
            lines += [f"   {k}. {s}" for k, s in enumerate(item.get("steps") or [], 1)]
            lines += [f"   - {s}" for s in item.get("items") or []]
    if caption:
        lines += ["", str(caption)]
    return "\n".join(lines) + "\n"


def _box_md(item: dict, via: str) -> str:
    """via: 'none' (the caller wrote it), 'tag' (names a branch) or 'arrow' (label on the arrow in)."""
    tag = ""
    if item.get("via") and via == "tag":
        tag = f"{item['via']}: "
    elif item.get("via") and via == "arrow":
        tag = f"_{item['via']}_ → "
    note = f" ({item['note']})" if item.get("note") else ""
    return f"{tag}**{item['box']}**{note}"


# ---------------------------------------------------------------- tree
def _load_tree(src: str) -> list[tuple[int, str, str]]:
    rows = []
    for n, line in enumerate(src.rstrip("\n").split("\n"), 1):
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2 or "\t" in line[:indent + 1]:
            raise DiagramError(f"tree line {n}: indent with two spaces per level")
        m = re.match(r"^(.*?)\s{2,}#\s*(.*)$", line.strip())
        name, note = (m.group(1), m.group(2)) if m else (line.strip(), "")
        rows.append((indent // 2, name.strip(), note.strip()))
    if not rows or rows[0][0] != 0:
        raise DiagramError("tree: the first line is the top folder, with no indent")
    for (d0, _, _), (d1, name, _) in zip(rows, rows[1:]):
        if d1 > d0 + 1:
            raise DiagramError(f"tree: '{name}' is indented two levels below its parent")
        if d1 == 0:
            raise DiagramError(f"tree: '{name}' is a second top folder; a tree has one")
    return rows


def tree_html(src: str) -> str:
    rows = _load_tree(src)
    out, depth = [], -1
    for d, name, note in rows:
        if d > depth:
            out.append("<ul>")
        else:
            out.append("</li>" + "</ul></li>" * (depth - d))
        depth = d
        cls = "vc-tree__dir" if name.endswith("/") else "vc-tree__file"
        out.append(f'<li><span class="{cls}">{esc(name)}</span>'
                   + (f'<span class="vc-tree__note">{esc(note)}</span>' if note else ""))
    out.append("</li>" + "</ul></li>" * depth + "</ul>")
    return f'<div class="vc-tree" role="group" aria-label="Folder tree">{"".join(out)}</div>\n'


def tree_markdown(src: str) -> str:
    """An ASCII tree in a text block: fine in a .md file, where no font is involved."""
    rows = _load_tree(src)
    lines = []
    for i, (d, name, note) in enumerate(rows):
        if d == 0:
            lines.append(name)
            continue
        prefix = ""
        for level in range(1, d):
            # Draw a bar at this level if an ancestor at this level has a later sibling.
            prefix += "│   " if _more_at(rows, i, level) else "    "
        prefix += "├── " if _more_at(rows, i, d) else "└── "
        lines.append(f"{prefix}{name}" + (f"   {note}" if note else ""))
    return "```text\n" + "\n".join(lines) + "\n```\n"


def _more_at(rows: list, i: int, level: int) -> bool:
    for d, _, _ in rows[i + 1:]:
        if d < level:
            return False
        if d == level:
            return True
    return False

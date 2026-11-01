#!/usr/bin/env python3
"""Build a static preview of the KiroCrew Cookbook.

Look: the violet-carbon-playbook skill. Carbon shape (square corners, flat tiles, 48px shell
header, no glow) in Kiro colors and fonts. The skill's tokens and overrides carry the whole look.

Source:  ../../content                               Markdown + frontmatter
Design:  ./assets/design-tokens                       tokens + overrides (Kiro Crew violet-carbon)
Output:  ./dist                                       landing, recipe index, one page per doc

Preview only. The real site is Fumadocs + Carbon, per the skill's references/setup.md.
That build needs Node, which this host does not have yet.

Needs markdown-it-py, PyYAML and Pygments.
    python3 build.py && python3 serve.py
"""
from __future__ import annotations

import datetime as dt
import html
import json
import posixpath
import re
import shutil
import sys
from pathlib import Path

import yaml
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

import concept_map
import dash_map
import diagrams
import where_is

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
CONTENT = PROJECT / "content"
DESIGN_TOKENS = HERE / "assets" / "design-tokens"
DIST = HERE / "dist"

SITE = "KiroCrew Cookbook"
DIFFICULTIES = ("beginner", "intermediate", "advanced")
SURFACES = {"dashboard": "Dashboard", "cli": "CLI", "channels": "Channels"}
REQUIRED = ("title", "description", "category", "difficulty", "time", "surfaces", "tags", "updated")
FONTS = ("https://fonts.googleapis.com/css2?family=Recursive:wght,CASL,MONO@300..1000,0..1,0..1"
         "&family=Geist:wght@300..700&family=Fragment+Mono&display=swap")
INSTALL = "curl -fsSL https://download.crew.kiro.dev/cli.sh | sh"

esc = html.escape

# Icons: stroke-only line icons, colored by currentColor. Product mark: a plain geometric glyph.
MARK = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path class="vc-mark-outer" d="M12 1.5 22.5 12 12 22.5 1.5 12z"/>'
        '<path class="vc-mark-inner" d="M12 8.25 15.75 12 12 15.75 8.25 12z"/></svg>')
BRAND = f"{MARK}<span><b>KiroCrew</b> Cookbook</span>"
I_COPY = ('<svg class="vc-icon" viewBox="0 0 16 16" aria-hidden="true"><rect x="5.5" y="5.5" width="8.5" height="8.5"/>'
          '<path d="M3.5 10.5h-2v-9h9v2"/></svg>')
I_SEARCH = ('<svg class="vc-icon" viewBox="0 0 16 16" aria-hidden="true"><circle cx="7" cy="7" r="4.75"/>'
            '<path d="m10.5 10.5 3.5 3.5"/></svg>')
I_GITHUB = ('<svg class="vc-icon" viewBox="0 0 16 16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.25">'
            '<path d="M6 15v-2.5c0-1 .5-1.5.5-1.5s-2.5-.5-2.5-3.5c0-1 .5-1.5.5-2 0-.5-.5-1.5 0-2.5 0 0 1 0 2 1 .5-.25 1.5-.5 2.5-.5s2 .25 2.5.5c1-1 2-1 2-1 .5 1 0 2 0 2.5 0 .5.5 1 .5 2 0 3-2.5 3.5-2.5 3.5s.5.5.5 1.5V15"/>'
            '<path d="M4 12c-1 .5-2 0-2.5-1"/></svg>')
I_DOC = ('<svg class="vc-icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 1.5h5l3.5 3.5v9.5H4z"/>'
         '<path d="M9 1.5V5h3.5M6.5 8.5h3.5M6.5 11h3.5"/></svg>')
I_ARROW = '<svg class="vc-icon" viewBox="0 0 16 16" aria-hidden="true"><path d="M2.5 8h11M9 3.5 13.5 8 9 12.5"/></svg>'
COPY_BTN = (f'<button type="button" class="vc-copy" data-copy aria-label="Copy to clipboard">{I_COPY}'
            '<span class="vc-copy__tip" aria-live="polite"></span></button>')


def fail(errors: list[str]) -> None:
    print("Build failed:", *errors, sep="\n  - ", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- content
def read_page(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    if not m:
        fail([f"{path}: no frontmatter"])
    meta = yaml.safe_load(m.group(1)) or {}
    if isinstance(meta.get("updated"), str):
        meta["updated"] = dt.date.fromisoformat(meta["updated"])
    slug = path.relative_to(CONTENT).with_suffix("").as_posix()
    return {"slug": slug, "meta": meta, "body": m.group(2), "src": path}


def validate(page: dict) -> list[str]:
    m, where, errs = page["meta"], page["src"].relative_to(PROJECT), []
    missing = [k for k in REQUIRED if m.get(k) in (None, "", [])]
    if missing:
        errs.append(f"{where}: missing {', '.join(missing)}")
    if len(str(m.get("title", ""))) > 60:
        errs.append(f"{where}: title longer than 60 chars")
    if len(str(m.get("description", ""))) > 140:
        errs.append(f"{where}: description longer than 140 chars")
    if m.get("difficulty") not in DIFFICULTIES:
        errs.append(f"{where}: difficulty must be one of {DIFFICULTIES}")
    bad = [s for s in m.get("surfaces") or [] if s not in SURFACES]
    if bad:
        errs.append(f"{where}: unknown surfaces {bad}")
    return errs


def load_site() -> dict:
    """Sections come from the root meta.json (one folder each, in order); pages from each folder's meta.json."""
    home = read_page(CONTENT / "index.md")
    sections, errs = [], []
    for sid in json.loads((CONTENT / "meta.json").read_text())["pages"]:
        if sid == "index":
            continue
        meta = json.loads((CONTENT / sid / "meta.json").read_text())
        pages = [read_page(CONTENT / sid / f"{n}.md") for n in meta["pages"]]
        sections.append({"id": sid, "title": meta["title"], "pages": pages})
        for p in pages:
            p["section"] = sid
            p["group"] = meta["title"]
    docs = [p for s in sections for p in s["pages"]]
    by_slug = {p["slug"]: p for p in docs}
    errs += [e for p in docs for e in validate(p)]
    listed = {p["src"] for p in docs} | {home["src"]}
    errs += [f"{p.relative_to(PROJECT)}: not listed in a meta.json" for p in CONTENT.rglob("*.md") if p not in listed]

    paths = home["meta"].get("paths") or []
    for path in paths:
        missing = [s for s in path["pages"] if s not in by_slug]
        if missing:
            errs.append(f"content/index.md: path '{path['id']}' names unknown pages {missing}")
        path["docs"] = [by_slug[s] for s in path["pages"] if s in by_slug]

    # Every relative .md link must land on a page this build writes.
    for p in [home, *docs]:
        for target in re.findall(r"\]\(([^)\s]+?\.md)(?:#[^)]*)?\)", p["body"]):
            if re.match(r"^[a-z]+:", target):
                continue
            resolved = (p["src"].parent / target).resolve()
            if resolved not in listed:
                errs.append(f"{p['src'].relative_to(PROJECT)}: broken link {target}")
    wayfinder = load_wayfinder(by_slug, errs)
    finder = None
    if (CONTENT / "find" / "tasks.yaml").exists():
        try:
            finder = where_is.load(PROJECT, by_slug)
        except where_is.WhereIsError as exc:
            errs.append(f"where-is: {exc}")
    dmap = None
    if not errs and (CONTENT / "find" / "map.yaml").exists():
        try:
            dmap = dash_map.load(PROJECT, by_slug, finder)
        except dash_map.MapError as exc:
            errs.append(f"dashboard-map: {exc}")
    if errs:
        fail(errs)

    for i, p in enumerate(docs):
        p["prev"] = docs[i - 1] if i > 0 else None
        p["next"] = docs[i + 1] if i + 1 < len(docs) else None
        # Where each reader path goes after this page (a page can sit on more than one path).
        p["path_next"] = []
        for path in paths:
            slugs = [d["slug"] for d in path["docs"]]
            if p["slug"] in slugs[:-1]:
                n = slugs.index(p["slug"]) + 1
                p["path_next"].append((path, path["docs"][n], n))
    recipes = next((s["pages"] for s in sections if s["id"] == "recipes"), [])
    return {"home": home, "sections": sections, "recipes": recipes, "docs": docs, "paths": paths,
            "finder": finder, "dmap": dmap, "wayfinder": wayfinder}


WAYFINDER_FENCE = re.compile(r"```find-your-way\n```\n?")


def load_wayfinder(by_slug: dict, errs: list[str]) -> list[dict]:
    """The "Which page do you need?" list (content/find/wayfinder.yaml). Every page in it must show it."""
    src = CONTENT / "find" / "wayfinder.yaml"
    if not src.exists():
        return []
    items = yaml.safe_load(src.read_text(encoding="utf-8")) or []
    for it in items:
        doc = by_slug.get(it.get("page"))
        if not doc or not it.get("name") or not it.get("job"):
            errs.append(f"content/find/wayfinder.yaml: '{it.get('page')}' needs a known page, a name and a job")
            continue
        it["doc"] = doc
        if not WAYFINDER_FENCE.search(doc["body"]):
            errs.append(f"{doc['src'].relative_to(PROJECT)}: listed in wayfinder.yaml but has no find-your-way block")
    for doc in by_slug.values():
        if WAYFINDER_FENCE.search(doc["body"]) and doc not in [it.get("doc") for it in items]:
            errs.append(f"{doc['src'].relative_to(PROJECT)}: has a find-your-way block but is not in wayfinder.yaml")
    return items


def wayfinder_html(items: list[dict], page: dict, depth: int) -> str:
    tiles = []
    for it in items:
        name = f'<span class="vc-wayfinder__name">{esc(it["name"])}</span>'
        job = f'<span class="vc-wayfinder__job">{esc(it["job"])}</span>'
        if it["doc"] is page:
            tiles.append(f'<li class="vc-wayfinder__item is-current" aria-current="page">{name}{job}'
                         '<span class="vc-wayfinder__here">You are here</span></li>')
        else:
            tiles.append(f'<li class="vc-wayfinder__item"><a class="vc-wayfinder__link" href="{href(it["doc"], depth)}">'
                         f'{name}{job}</a></li>')
    return (f'<nav class="vc-wayfinder" aria-label="Which page do you need?"><p class="vc-label">Which page do you need?</p>'
            f'<ol class="vc-wayfinder__list">{"".join(tiles)}</ol></nav>\n')


def wayfinder_markdown(items: list[dict], page: dict) -> str:
    here = posixpath.dirname(page["slug"]) or "."
    lines = []
    for it in items:
        if it["doc"] is page:
            lines.append(f"- **{it['name']}** (this page): {it['job'].lower()}.")
        else:
            link = posixpath.relpath(it["doc"]["slug"] + ".md", here)
            lines.append(f"- [{it['name']}]({link}): {it['job'].lower()}.")
    return "Which page do you need?\n\n" + "\n".join(lines) + "\n"


def section_href(section: dict, depth: int) -> str:
    """Recipes have their own filterable index; other sections open on their first page."""
    if section["id"] == "recipes":
        return f"{rel(depth)}recipes/index.html"
    return href(section["pages"][0], depth)


# ---------------------------------------------------------------- markdown
def inline_text(tok) -> str:
    return "".join(c.content if c.type in ("text", "code_inline") else " " if c.type == "softbreak" else ""
                   for c in tok.children or [])


def slugify(text: str, seen: set[str]) -> str:
    s = re.sub(r"[\s_]+", "-", re.sub(r"[^\w\s-]", "", text.lower()).strip()) or "section"
    base, n = s, 2
    while s in seen:
        s, n = f"{base}-{n}", n + 1
    seen.add(s)
    return s


def code_html(code: str, lang: str) -> str:
    lexer = None
    if lang and lang != "text":
        try:
            lexer = get_lexer_by_name(lang)
        except ClassNotFound:
            lexer = None
    body = highlight(code, lexer, HtmlFormatter(nowrap=True)) if lexer else esc(code)
    return f'<div class="vc-code"><pre><code>{body.rstrip()}</code></pre>{COPY_BTN}</div>\n'


def prompt_html(code: str) -> str:
    return ('<div class="vc-prompt"><p class="vc-prompt__label">Prompt</p><div class="vc-prompt__box">'
            f'<pre><code>{esc(code.rstrip())}</code></pre>{COPY_BTN}</div></div>\n')


def make_md() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": False}).enable(["table", "strikethrough"])

    def fence(self, tokens, idx, options, env):
        tok = tokens[idx]
        words = tok.info.strip().split()
        lang = words[0] if words else ""
        if lang in ("where-is", "where-is-table", "dashboard-map", "dashboard-map-table", "concept-map", "find-your-way"):
            return f"<!--{lang}-->\n"
        if lang in ("flow", "tree"):
            try:
                return diagrams.flow_html(tok.content, md.renderInline) if lang == "flow" else diagrams.tree_html(tok.content)
            except diagrams.DiagramError as exc:
                fail([f"{env.get('slug', '?')}: {exc}"])
        return prompt_html(tok.content) if lang == "prompt" else code_html(tok.content, lang)

    def heading_open(self, tokens, idx, options, env):
        out = self.renderToken(tokens, idx, options, env)
        step = (tokens[idx].meta or {}).get("step")
        if step:
            out += (f'<span class="vc-step-num" aria-hidden="true">{int(step):02d}</span>'
                    f'<span class="vc-sr">Step {step}: </span>')
        return out

    md.add_render_rule("fence", fence)
    md.add_render_rule("heading_open", heading_open)
    md.add_render_rule("table_open", lambda self, t, i, o, e: '<div class="vc-table-wrap"><table>\n')
    md.add_render_rule("table_close", lambda self, t, i, o, e: "</table></div>\n")
    return md


MD = make_md()


def render_body(body: str, seen: set[str], slug: str = "?") -> tuple[str, list[tuple[int, str, str]]]:
    """Render Markdown; return HTML and TOC entries (level, label, id)."""
    tokens = MD.parse(body, {})
    toc = []
    for i, tok in enumerate(tokens):
        if tok.type == "inline":
            for c in tok.children or []:
                if c.type == "link_open":
                    href = c.attrGet("href") or ""
                    if not re.match(r"^[a-z]+:", href):
                        c.attrSet("href", re.sub(r"\.md(?=$|#)", ".html", href))
        if tok.type == "heading_open" and tok.tag in ("h2", "h3"):
            inline = tokens[i + 1]
            label = inline_text(inline).strip()
            hid = slugify(label, seen)
            tok.attrSet("id", hid)
            toc.append((int(tok.tag[1]), label, hid))
            m = re.match(r"^(\d+)\.\s+", label)
            if tok.tag == "h3" and m and inline.children and inline.children[0].type == "text":
                tok.attrSet("class", "vc-step-h")
                tok.meta = {"step": m.group(1)}
                first = inline.children[0]
                first.content = re.sub(r"^\d+\.\s+", "", first.content)
    return wrap_steps(MD.renderer.render(tokens, MD.options, {"slug": slug})), toc


def wrap_steps(markup: str) -> str:
    """Group consecutive numbered-step sections so each gets its number column and rule."""
    out, group = [], []
    for seg in re.split(r"(?=<h[23][\s>])", markup):
        if seg.startswith("<h3") and 'class="vc-step-h"' in seg.split(">", 1)[0]:
            group.append(f'<div class="vc-step">{seg}</div>')
            continue
        if group:
            out.append(f'<div class="vc-steps-group">{"".join(group)}</div>')
            group = []
        out.append(seg)
    if group:
        out.append(f'<div class="vc-steps-group">{"".join(group)}</div>')
    return "".join(out)


# ---------------------------------------------------------------- shared chrome
def rel(depth: int) -> str:
    return "../" * depth


def href(page: dict, depth: int) -> str:
    return f"{rel(depth)}{page['slug']}.html"


def fmt_date(d: dt.date) -> str:
    return f"{d:%b} {d.day}, {d.year}"


def head(title: str, description: str, depth: int) -> str:
    r = rel(depth)
    return f"""<!doctype html>
<html lang="en" class="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="color-scheme" content="dark">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{esc(FONTS)}">
<link rel="stylesheet" href="{r}assets/vc-tokens.css">
<link rel="stylesheet" href="{r}assets/vc-overrides.css">
<link rel="stylesheet" href="{r}assets/site.css">
<link rel="alternate" type="text/plain" href="{r}llms.txt" title="llms.txt">
</head>
<body>
<a class="vc-skip" href="#main">Skip to content</a>
"""


def nav(depth: int, current: str = "") -> str:
    r = rel(depth)
    cur = lambda key: ' aria-current="page"' if key == current else ""
    return f"""<header class="vc-nav"><div class="vc-nav__inner">
<a class="vc-brand" href="{r}index.html">{BRAND}</a>
<nav aria-label="Main" class="vc-nav__menu"><ul class="vc-nav__links">
<li><a href="{r}start/install.html"{cur("start")}>Get started</a></li>
<li><a href="{r}find/dashboard-map.html"{cur("find")}>Find your way</a></li>
<li><a href="{r}concepts/what-kirocrew-is.html"{cur("concepts")}>Concepts</a></li>
<li><a href="{r}apps/what-apps-are.html"{cur("apps")}>Apps</a></li>
<li><a href="{r}recipes/index.html"{cur("recipes")}>Recipes</a></li>
<li><a href="{r}llms.txt">llms.txt</a></li>
</ul></nav>
<div class="vc-nav__end">
<a class="vc-nav__action" href="{r}recipes/index.html#search" data-search-href="{r}recipes/index.html#search" aria-label="Search recipes" title="Search recipes (⌘K)">{I_SEARCH}</a>
<a class="vc-nav__action" href="https://github.com/requix/kirocrew-cookbook" aria-label="GitHub repository" title="View on GitHub">{I_GITHUB}</a>
<a class="vc-btn vc-btn--primary vc-nav__cta" href="{r}index.html#paths">Start {I_ARROW}</a>
</div></div></header>
"""


def footer(site: dict, depth: int) -> str:
    links = lambda pages: "".join(f'<li><a href="{href(p, depth)}">{esc(p["meta"]["title"])}</a></li>' for p in pages)
    cols = "".join(f'<div><p class="vc-label">{esc(s["title"])}</p><ul>{links(s["pages"])}</ul></div>' for s in site["sections"])
    return f"""<footer class="vc-footer"><div class="vc-wrap vc-footer__grid">
<div class="vc-footer__brand"><a class="vc-brand" href="{rel(depth)}index.html">{BRAND}</a>
<p>Recipes from real work with KiroCrew. Checked against the KiroCrew source, not written from memory.</p></div>
{cols}
<div><p class="vc-label">For agents</p><ul><li><a href="{rel(depth)}llms.txt">llms.txt</a></li>
<li><a href="{rel(depth)}start/first-hour.md">Markdown per page</a></li></ul></div>
<div><p class="vc-label">Contribute</p><ul><li><a href="https://github.com/requix/kirocrew-cookbook">GitHub</a></li>
<li><a href="https://github.com/requix/kirocrew-cookbook/issues/new?template=bug_report.yml">Report an issue</a></li>
<li><a href="https://github.com/requix/kirocrew-cookbook/issues/new?template=new_recipe.yml">Suggest a recipe</a></li></ul></div>
</div></footer>
<script src="{rel(depth)}assets/site.js"></script>
</body>
</html>
"""


def card_id(page: dict) -> str:
    return page["slug"].replace("/", "-")


def card(page: dict, depth: int, level: int = 3) -> str:
    m = page["meta"]
    cls = "vc-card vc-rcard" + (" vc-featured" if m.get("featured") else "")
    tags = "".join(f'<li class="vc-tag">{esc(t)}</li>' for t in m["tags"])
    return f"""<a class="{cls}" id="card-{card_id(page)}" href="{href(page, depth)}">
<span class="vc-label">{esc(m["category"])}</span>
<h{level} class="vc-rcard__title">{esc(m["title"])}</h{level}>
<p class="vc-rcard__desc">{esc(m["description"])}</p>
<div class="vc-rcard__foot"><ul class="vc-tags" aria-label="Tags">{tags}</ul>
<div class="vc-rcard__row"><div class="vc-meta"><span class="vc-dot vc-dot--{m["difficulty"]}">{m["difficulty"].capitalize()}</span><span>{esc(str(m["time"]))}</span></div>
<span class="vc-rcard__arrow">{I_ARROW}</span></div></div>
</a>"""


def toc_list(toc: list[tuple[int, str, str]]) -> str:
    items = "".join(f'<li class="{"is-sub" if lvl == 3 else ""}"><a href="#{hid}">{esc(label)}</a></li>' for lvl, label, hid in toc)
    return f"<ul>{items}</ul>"


def sidenav(site: dict, current: dict, depth: int) -> str:
    def group(title, pages):
        lis = "".join(
            f'<li><a href="{href(p, depth)}"'
            + (' class="vc-nav-active" aria-current="page"' if p is current else "")
            + f'>{esc(p["meta"]["title"])}</a></li>' for p in pages)
        return f'<p class="vc-sidenav__group">{title}</p><ul>{lis}</ul>'
    return f'<nav class="vc-sidenav" aria-label="Cookbook pages">{"".join(group(s["title"], s["pages"]) for s in site["sections"])}</nav>'


# ---------------------------------------------------------------- pages
TERMINAL = """<div class="vc-term">
<div class="vc-term__bar">Terminal · your first hour</div>
<pre><code><span class="t-c"># 1. install: a signed, verified build</span>
<span class="t-p">$ </span>curl -fsSL https://download.crew.kiro.dev/cli.sh | sh

<span class="t-c"># 2. start the gateway and leave it running</span>
<span class="t-p">$ </span>kirocrew gateway

<span class="t-c"># 3. open the dashboard</span>
<span class="t-f">http://localhost:5476</span>

<span class="t-c"># 4. give it real work, not "hello"</span>
<span class="t-a">› </span><span class="t-s">Every weekday at 8am, check my repo for PRs with no review and send me a summary.</span></code></pre>
</div>"""


def path_tile(path: dict) -> str:
    steps = "".join(
        f'<li><a href="{href(p, 0)}"><span class="vc-path__num" aria-hidden="true">{i:02d}</span>'
        f'<span class="vc-path__page">{esc(p["meta"]["title"])}</span><small>{esc(str(p["meta"]["time"]))}</small></a></li>'
        for i, p in enumerate(path["docs"], 1))
    first = path["docs"][0]
    return f"""<article class="vc-card vc-path" id="path-{esc(path["id"])}" aria-labelledby="path-{esc(path["id"])}-h">
<p class="vc-label">{esc(path["label"])}</p>
<h3 class="vc-path__title" id="path-{esc(path["id"])}-h">{esc(path["title"])}</h3>
<p class="vc-path__summary">{esc(path["summary"])}</p>
<ol class="vc-path__steps" aria-label="Pages on this path, in order">{steps}</ol>
<a class="vc-btn vc-btn--primary vc-path__cta" href="{href(first, 0)}">Start with {esc(first["meta"]["title"])} {I_ARROW}</a>
</article>"""


def landing(site: dict) -> str:
    home, docs = site["home"], site["docs"]
    m = home["meta"]
    order = {p["slug"]: i for i, p in enumerate(docs)}
    newest = sorted(docs, key=lambda p: (-p["meta"]["updated"].toordinal(), order[p["slug"]]))[:6]
    new_items = "".join(f'<li><a href="{href(p, 0)}"><span>{esc(p["meta"]["title"])}</span><small>{esc(str(p["meta"]["time"]))}</small></a></li>' for p in newest)
    paths = "".join(path_tile(p) for p in site["paths"])
    sec_tiles = "".join(
        f'<li><a class="vc-card vc-cat" href="{section_href(s, 0)}">'
        f'<span class="vc-cat__name">{esc(s["title"])}</span><span class="vc-cat__count">{len(s["pages"])} page{"s" if len(s["pages"]) != 1 else ""}</span>'
        f'<span class="vc-rcard__arrow">{I_ARROW}</span></a></li>'
        for s in site["sections"])
    who = re.search(r"## Who this is for\n\n(.*?)(?=\n## |\n---|\Z)", home["body"], re.S)
    audience = MD.render(who.group(1).strip()) if who else ""
    ordered = sorted(docs, key=lambda p: (not p["meta"].get("featured"), order[p["slug"]]))
    return (head(m["title"], m["description"], 0) + nav(0) + f"""<main id="main">
<section class="vc-hero"><div class="vc-wrap">
<div class="vc-hero__lines vc-grid-lines" aria-hidden="true"></div>
<div class="vc-hero__grid">
<div>
<p class="vc-label">KiroCrew Cookbook / First edition</p>
<h1>{esc(m["hero"])}</h1>
<p class="vc-hero__lead">{esc(m["description"])} Pick the path that matches where you are starting from.</p>
<div class="vc-btn-set">
<a class="vc-btn vc-btn--primary" href="#paths">Pick your path {I_ARROW}</a>
<a class="vc-btn vc-btn--tertiary" href="recipes/index.html">Browse recipes {I_ARROW}</a>
</div>
<div class="vc-snippet"><span class="vc-snippet__prompt" aria-hidden="true">$</span><code>{esc(INSTALL)}</code>{COPY_BTN}</div>
</div>
<div><aside class="vc-card vc-new" aria-labelledby="new-h">
<span class="vc-badge">New</span>
<h2 id="new-h" class="vc-new__title">What's new</h2>
<ul>{new_items}</ul>
</aside></div>
</div>
</div></section>

<section class="vc-section vc-paths-section" id="paths" aria-labelledby="paths-h"><div class="vc-wrap">
<div class="vc-section__head"><div><p class="vc-label">Pick your path</p><h2 id="paths-h">Where are you starting from?</h2></div></div>
<div class="vc-paths">{paths}</div>
</div></section>

<section class="vc-section"><div class="vc-wrap">{TERMINAL}</div></section>

<section class="vc-section"><div class="vc-wrap">
<div class="vc-section__head"><div><p class="vc-label">By section</p><h2>Browse the cookbook</h2></div>
<a href="recipes/index.html">All recipes →</a></div>
<ul class="vc-catgrid vc-catgrid--sections">{sec_tiles}</ul>
</div></section>

<section class="vc-section"><div class="vc-wrap">
<div class="vc-section__head"><div><p class="vc-label">Who this is for</p><h2>New to KiroCrew, with or without Kiro</h2></div></div>
<div class="vc-audience">{audience}</div>
</div></section>

<section class="vc-section"><div class="vc-wrap">
<div class="vc-section__head"><div><p class="vc-label">All pages</p><h2>Everything so far</h2></div></div>
<div class="vc-grid">{"".join(card(p, 0) for p in ordered)}</div>
</div></section>
</main>
""" + footer(site, 0))


def recipe_index(site: dict) -> str:
    recipes = sorted(site["recipes"], key=lambda p: (not p["meta"].get("featured"), -p["meta"]["updated"].toordinal()))
    tags = sorted({t for p in recipes for t in p["meta"]["tags"]})
    tag_btns = "".join(f'<li><button type="button" class="vc-tag" data-tag="{esc(t)}" aria-pressed="false">{esc(t)}</button></li>' for t in tags)
    data = [{"slug": card_id(p), "title": p["meta"]["title"], "description": p["meta"]["description"],
             "category": p["meta"]["category"], "tags": p["meta"]["tags"], "surfaces": p["meta"]["surfaces"]}
            for p in recipes]
    data_json = json.dumps(data).replace("</", "<\\/")
    return (head(f"Recipes · {SITE}", "Every recipe in the KiroCrew Cookbook.", 1) + nav(1, "recipes") + f"""<main id="main" class="vc-wrap">
<div class="vc-index-head"><h1>Recipes</h1><p id="recipe-count" aria-live="polite">{len(recipes)} recipes</p></div>
<div class="vc-filters" role="search">
<label class="vc-search"><span class="vc-sr">Search recipes</span>{I_SEARCH}<input id="recipe-search" type="search" placeholder="Search recipes" autocomplete="off"></label>
<div class="vc-switch" role="group" aria-label="Surface">
<button type="button" data-surface="all" aria-pressed="true">All</button>
<button type="button" data-surface="dashboard" aria-pressed="false">Dashboard</button>
<button type="button" data-surface="cli" aria-pressed="false">CLI</button>
</div>
</div>
<div class="vc-tagbar"><ul aria-label="Filter by tag">{tag_btns}</ul></div>
<div id="recipe-grid" class="vc-grid">{"".join(card(p, 1, level=2) for p in recipes)}</div>
<div id="recipe-empty" class="vc-card vc-empty" hidden><p>No recipes match.</p>
<button type="button" class="vc-btn vc-btn--ghost vc-btn--sm" id="recipe-clear">Clear filters</button></div>
<script type="application/json" id="recipe-index">{data_json}</script>
</main>
""" + footer(site, 1))


def doc_page(site: dict, page: dict) -> str:
    m = page["meta"]
    depth = page["slug"].count("/")
    r = rel(depth)
    seen: set[str] = set()
    prereq = ""
    toc: list[tuple[int, str, str]] = []
    if m.get("prerequisites"):
        pid = slugify("Before you start", seen)
        items = "".join(f"<li>{MD.renderInline(str(x))}</li>" for x in m["prerequisites"])
        prereq = f'<h2 id="{pid}">Before you start</h2><ul class="vc-checklist">{items}</ul>'
        toc.append((2, "Before you start", pid))
    body, body_toc = render_body(page["body"], seen, page["slug"])
    toc += body_toc
    # Skill order: outcome paragraph first, then "Before you start".
    if prereq and body.startswith("<p>") and "</p>" in body:
        cut = body.index("</p>") + len("</p>")
        body, prereq = body[:cut] + prereq + body[cut:], ""
    surfaces = ", ".join(SURFACES[s] for s in m["surfaces"])
    date = fmt_date(m["updated"])
    md_name = page["slug"].rsplit("/", 1)[-1] + ".md"
    section = next(s for s in site["sections"] if s["id"] == page["section"])
    group = f'<li><a href="{section_href(section, depth)}">{esc(section["title"])}</a></li>'
    pager = ""
    if page["prev"]:
        pager += (f'<a class="vc-card is-prev" href="{href(page["prev"], depth)}"><span class="vc-label">← Previous</span>'
                  f'<span class="vc-rcard__title">{esc(page["prev"]["meta"]["title"])}</span></a>')
    if page["next"]:
        pager += (f'<a class="vc-card is-next" href="{href(page["next"], depth)}"><span class="vc-label">Next →</span>'
                  f'<span class="vc-rcard__title">{esc(page["next"]["meta"]["title"])}</span></a>')
    onpath = "".join(
        f'<a class="vc-card vc-onpath__item" href="{href(nxt, depth)}">'
        f'<span class="vc-label">{esc(path["label"])} · step {n + 1} of {len(path["docs"])}</span>'
        f'<span class="vc-rcard__title">{esc(nxt["meta"]["title"])}</span>'
        f'<span class="vc-rcard__arrow">{I_ARROW}</span></a>'
        for path, nxt, n in page["path_next"])
    if onpath:
        onpath = f'<nav class="vc-onpath" aria-label="Next on your path"><p class="vc-label">Next on your path</p><div class="vc-onpath__grid">{onpath}</div></nav>'
    if "<!--find-your-way-->" in body:
        body = body.replace("<!--find-your-way-->", wayfinder_html(site["wayfinder"], page, depth))
    if "<!--where-is" in body:
        body = (body.replace("<!--where-is-->", where_is.widget_html(site["finder"], r))
                    .replace("<!--where-is-table-->", where_is.fallback_table(site["finder"], r)))
    if "<!--concept-map-->" in body:
        try:
            body = body.replace("<!--concept-map-->", concept_map.widget_html(concept_map.load(PROJECT, page["body"]), r))
        except concept_map.ConceptMapError as exc:
            fail([f"concept-map: {exc}"])
    if "<!--dashboard-map" in body:
        body = (body.replace("<!--dashboard-map-->", dash_map.widget_html(site["dmap"], r))
                    .replace("<!--dashboard-map-table-->", dash_map.fallback_table(site["dmap"])))
    wide = m.get("layout") == "wide"
    toc_aside = "" if wide else f'<aside class="vc-toc" aria-label="On this page"><p class="vc-label">On this page</p>{toc_list(toc)}</aside>'
    current = page["section"]
    return (head(f"{m['title']} · {SITE}", m["description"], depth) + nav(depth, current) + f"""<div class="vc-docs{' vc-docs--wide' if wide else ''}">
<aside class="vc-sidebar">{sidenav(site, page, depth)}</aside>
<main id="main" class="vc-main-col">
<details class="vc-drawer"><summary>Cookbook menu</summary>{sidenav(site, page, depth)}</details>
<div class="vc-main"><article class="vc-article">
<header class="vc-page-head">
<div class="vc-page-head__top">
<nav aria-label="Breadcrumb"><ol class="vc-crumbs"><li><a href="{r}index.html">Cookbook</a></li>{group}<li aria-current="page">{esc(m["title"])}</li></ol></nav>
<div class="vc-actions">
<button type="button" class="vc-btn vc-btn--ghost vc-btn--sm" data-copy-page="{md_name}"><span data-label>Copy page</span>{I_COPY}</button>
<a class="vc-btn vc-btn--ghost vc-btn--sm" href="{md_name}">View as Markdown {I_DOC}</a>
</div>
</div>
<h1 class="vc-page-title">{esc(m["title"])}</h1>
<div class="vc-meta"><span class="vc-dot vc-dot--{m["difficulty"]}">{m["difficulty"].capitalize()}</span><span>{esc(str(m["time"]))}</span><span>{surfaces}</span><span>Updated {date}</span></div>
<p class="vc-lead">{esc(m["description"])}</p>
<details class="vc-toc-inline"><summary>On this page</summary>{toc_list(toc)}</details>
</header>
<div class="vc-prose">{prereq}{body}</div>
{onpath}
<p class="vc-updated">Last updated {date}</p>
<nav class="vc-pager" aria-label="Previous and next">{pager}</nav>
</article></div>
</main>
{toc_aside}
</div>
""" + footer(site, depth))


def page_markdown(page: dict, finder: dict | None = None, dmap: dict | None = None,
                  wayfinder: list[dict] | None = None) -> str:
    """Processed Markdown for agents: title + description + body, no frontmatter."""
    m = page["meta"]
    body = page["body"]
    if wayfinder:
        body = WAYFINDER_FENCE.sub(lambda _: wayfinder_markdown(wayfinder, page), body)
    if finder:
        body = re.sub(r"```where-is\n```\n?", "", body)
        body = re.sub(r"```where-is-table\n```\n?", lambda _: where_is.markdown_table(finder), body)
    body = re.sub(r"```concept-map\n```\n?", "", body)
    body = re.sub(r"```flow\n(.*?)```\n?", lambda m: diagrams.flow_markdown(m.group(1)), body, flags=re.S)
    body = re.sub(r"```tree\n(.*?)```\n?", lambda m: diagrams.tree_markdown(m.group(1)), body, flags=re.S)
    if dmap:
        body = re.sub(r"```dashboard-map\n```\n?", "", body)
        body = re.sub(r"```dashboard-map-table\n```\n?", lambda _: dash_map.markdown_table(dmap), body)
    pre = "".join(f"- [ ] {x}\n" for x in m.get("prerequisites") or [])
    pre = f"## Before you start\n\n{pre}\n" if pre else ""
    return f"# {m['title']}\n\n> {m['description']}\n\n{pre}{body.lstrip()}"


def llms_txt(site: dict) -> str:
    line = lambda p: f"- [{p['meta']['title']}]({p['slug']}.md): {p['meta']['description']}"
    out = [f"# {SITE}", "", f"> {site['home']['meta']['description']}", ""]
    for s in site["sections"]:
        out += [f"## {s['title']}", *map(line, s["pages"]), ""]
    return "\n".join(out)


# ---------------------------------------------------------------- build
def main() -> None:
    site = load_site()
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    for s in site["sections"]:
        (DIST / s["id"]).mkdir(exist_ok=True)
    for name in ("vc-tokens.css", "vc-overrides.css"):
        shutil.copy(DESIGN_TOKENS / name, DIST / "assets" / name)
    for name in ("site.css", "site.js", "where-is.css", "where-is.js", "kc-drawing.js", "dashboard-map.js", "concept-map.js", "concept-map.css"):
        shutil.copy(HERE / "assets" / name, DIST / "assets" / name)

    out = {"index.html": landing(site), "recipes/index.html": recipe_index(site), "llms.txt": llms_txt(site)}
    for p in site["docs"]:
        out[f"{p['slug']}.html"] = doc_page(site, p)
        out[f"{p['slug']}.md"] = page_markdown(p, site["finder"], site["dmap"], site["wayfinder"])
    for rel_path, text in out.items():
        (DIST / rel_path).write_text(text, encoding="utf-8")
    print(f"Built {len(out)} files into {DIST}")


if __name__ == "__main__":
    main()

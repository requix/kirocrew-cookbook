"""Pin the dashboard's own English UI text the cookbook quotes (tab names and descriptions).

The Dashboard map shows each Customize and Settings tab with the one-line
description the dashboard itself shows. Those strings live in the dashboard's
translation files, which the UI index does not carry, so this copies the few
the cookbook needs from a KiroCrew source checkout.

    python3 pin_ui_text.py /path/to/KiroCrew

Writes ../data/ui-text.json with the checkout's commit, so you know which
build the words came from.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "ui-text.json"
# Keys the cookbook uses. Anything else in the catalog is left out.
WANT = re.compile(
    r"^(pages\.capabilitiesPage\.\w+_(label|description)"
    r"|pages\.capabilitiesPage\.group_\w+"
    r"|settings\.tabs\.[\w-]+\.(label|description)"
    r"|privacyDisclosure\.settings(Label|Description)"
    r"|components\.chatInput\.optimize_prompt)$"
)


def flatten(d: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(flatten(v, key))
        elif isinstance(v, str):
            out[key] = v
    return out


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    repo = Path(sys.argv[1]).expanduser().resolve()
    locales = repo / "website" / "src" / "i18n" / "locales"
    strings: dict[str, str] = {}
    # en.manual.json is the hand-written base; en.json (generated) wins where both define a key.
    for name in ("en.manual.json", "en.json"):
        path = locales / name
        if path.exists():
            strings.update(flatten(json.loads(path.read_text(encoding="utf-8"))))
    picked = {k: v for k, v in sorted(strings.items()) if WANT.match(k)}
    if not picked:
        sys.exit(f"no matching strings under {locales}")
    commit = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"source_commit": commit, "strings": picked}, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    print(f"Pinned {len(picked)} strings from KiroCrew {commit} into {OUT}")


if __name__ == "__main__":
    main()

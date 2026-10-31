"""Pin KiroCrew's own UI location index into the cookbook repo.

The "Where is…?" page reads its labels and click paths from this file, so the
answers match the dashboard of one known KiroCrew release. Re-run after you
upgrade KiroCrew, rebuild, and fix whatever the build reports as gone.

    python3 pin_ui_index.py                       # from the installed kirocrew
    python3 pin_ui_index.py /path/to/ui-index.generated.json 0.11.0

Writes ../data/ui-index.json: the locations, the English labels and the
condition texts. Other locales and guide internals are dropped to keep it small.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "ui-index.json"
KEEP = ("id", "kind", "label_key", "label_kind", "placements", "setting_id", "state_labels")


def installed_index() -> tuple[Path, str]:
    """Find ui-index.generated.json inside the kirocrew package that `kirocrew` runs."""
    exe = shutil.which("kirocrew")
    if not exe:
        sys.exit("kirocrew is not on PATH; pass the index path and version instead")
    version = subprocess.run([exe, "--version"], capture_output=True, text=True).stdout.split()[-1]
    venv = Path(exe).resolve().parent.parent
    hits = sorted(venv.glob("lib/python3*/site-packages/kiro_crew/docs/ui-index.generated.json"))
    if not hits:
        sys.exit(f"no ui-index.generated.json under {venv}")
    return hits[0], version


def main() -> None:
    if len(sys.argv) == 3:
        src, version = Path(sys.argv[1]), sys.argv[2]
    else:
        src, version = installed_index()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-.\w]*)", version):
        sys.exit(f"unexpected version string: {version!r}")
    raw = json.loads(src.read_text(encoding="utf-8"))
    locs = []
    for loc in raw["locations"]:
        if loc.get("tier") == "auto":  # page known, exact place unknown: not precise enough to draw
            continue
        item = {k: loc[k] for k in KEEP if k in loc}
        terms = (loc.get("terms") or {}).get("en")
        if terms:
            item["terms"] = terms
        locs.append(item)
    out = {
        "kirocrew_version": version,
        "build_digest": raw.get("build_digest"),
        "schema_version": raw.get("schema_version"),
        "conditions": dict(raw["conditions"]),
        "labels": raw["labels"]["en"],
        "locations": locs,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Pinned {len(locs)} locations from KiroCrew {version} into {OUT}")


if __name__ == "__main__":
    main()

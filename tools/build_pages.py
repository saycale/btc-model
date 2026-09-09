#!/usr/bin/env python3
"""Build deployable, self-contained HTML pages from shared model sources.

The deployed HTML deliberately inlines model-core.js and observations.js.
This prevents a GitHub Pages/CDN propagation race where a new page is served
before one of its required JavaScript assets.  The shared files remain the
canonical editable sources; this script is the only allowed way to refresh the
generated runtime block in index.html and ru.html.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = (ROOT / "model-core.js").read_text(encoding="utf-8").strip()
DATA = (ROOT / "data" / "observations.js").read_text(encoding="utf-8").strip()
DECL = "const {OBS_START,OBS,OBS_LAST_DATE,OBS_LAST_PROVISIONAL}=window.BTC_MODEL_DATA;"


def generated_block() -> str:
    return "<script>\n/* GENERATED_RUNTIME_START — do not edit; run tools/build_pages.py */\n" + CORE + "\n" + DATA + "\n/* GENERATED_RUNTIME_END */\n" + DECL + "\n"


def render(page: str) -> str:
    if "GENERATED_RUNTIME_START" in page:
        pattern = r'<script>\n/\* GENERATED_RUNTIME_START.*?' + re.escape(DECL) + r'\n'
    else:
        pattern = r'<script src="model-core\.js"></script>\n<script src="data/observations\.js"></script>\n<script>\n.*?' + re.escape(DECL) + r'\n'
    out, n = re.subn(pattern, generated_block(), page, count=1, flags=re.S)
    if n != 1:
        raise RuntimeError("could not locate runtime block")
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="fail if generated blocks are stale")
    args = p.parse_args()
    stale = []
    for name in ("index.html", "ru.html"):
        path = ROOT / name
        current = path.read_text(encoding="utf-8")
        built = render(current)
        if current != built:
            stale.append(name)
            if not args.check:
                path.write_text(built, encoding="utf-8")
    if stale and args.check:
        raise SystemExit("generated runtime is stale: " + ", ".join(stale) + "; run python3 tools/build_pages.py")
    print("ok: generated runtime " + ("checked" if args.check else "updated") + (" (" + ", ".join(stale) + ")" if stale else ""))


if __name__ == "__main__":
    main()

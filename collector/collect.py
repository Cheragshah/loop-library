#!/usr/bin/env python3
"""Run all collectors, merge into the catalog, and publish data for the app.

    python3 collector/collect.py

Outputs:
    collector/data/loops.json   canonical store (deduped, with trending scores)
    public/loops.json           data the Vite app reads (committed by CI)
    public/loop-library.xlsx    downloadable Excel sheet served by the site
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import store
from collectors import forwardfuture, manual, social
from export_xlsx import export as export_xlsx

# The Vite app reads its data from public/. CI commits these files.
PUBLIC = Path(__file__).resolve().parent.parent / "public"

COLLECTORS = [
    ("forwardfuture", forwardfuture.collect),
    ("social", social.collect),
    ("manual", manual.collect),
]


def main() -> int:
    collected: list[dict] = []
    print("Collecting loops…")
    for name, fn in COLLECTORS:
        try:
            collected.extend(fn())
        except Exception as e:
            print(f"  [{name}] collector crashed: {e}")

    if not collected:
        print("No loops collected (check network / sources).")

    catalog = store.merge(store.load(), collected)
    loops = store.save(catalog)

    xlsx = export_xlsx(loops)

    PUBLIC.mkdir(parents=True, exist_ok=True)
    # The app reads public/loops.json; strip internal (_-prefixed) fields.
    public_loops = [{k: v for k, v in l.items() if not k.startswith("_")} for l in loops]
    (PUBLIC / "loops.json").write_text(
        store.json.dumps(public_loops, indent=2, ensure_ascii=False)
    )
    shutil.copy(xlsx, PUBLIC / "loop-library.xlsx")

    print(f"\nCatalog: {len(loops)} loops total")
    print(f"  Canonical -> {store.STORE_PATH}")
    print(f"  App data  -> {PUBLIC / 'loops.json'}")
    print(f"  Excel     -> {PUBLIC / 'loop-library.xlsx'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

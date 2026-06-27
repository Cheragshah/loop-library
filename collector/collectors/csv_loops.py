"""Load loops from a curated CSV (collector/data/loops.csv).

The CSV uses: category, name, command (the /slash invocation), prompt
(the full loop), description, slug. We map `prompt` -> the library's full
command and keep the /slash invocation in the `slash` field.
"""

from __future__ import annotations

import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "loops.csv"


def collect() -> list[dict]:
    if not CSV_PATH.exists():
        return []
    out = []
    with CSV_PATH.open(newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            prompt = (row.get("prompt") or "").strip()
            if not name or not prompt:
                continue
            out.append(
                {
                    "name": name,
                    "command": prompt,  # the full, repurposable loop
                    "slash": (row.get("command") or "").strip(),
                    "what_it_does": (row.get("description") or "").strip(),
                    "category": (row.get("category") or "").strip(),
                    "author": "",
                    "source": "Loop Library CSV",
                    "source_url": "",
                    "tags": [(row.get("slug") or "").strip()],
                }
            )
    print(f"  [csv] loops.csv: {len(out)} loops")
    return out

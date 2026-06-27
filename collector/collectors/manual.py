"""Manual + AI-assisted curation.

You drop loops you find anywhere into data/inbox.json; they flow into the
catalog like any scraped source, but marked as hand-curated (highest trust).
See data/inbox.json for the expected shape — it's just a list of loop objects.
"""

from __future__ import annotations

import json
from pathlib import Path

INBOX = Path(__file__).resolve().parent.parent / "data" / "inbox.json"


def collect() -> list[dict]:
    if not INBOX.exists():
        return []
    try:
        entries = json.loads(INBOX.read_text())
    except json.JSONDecodeError as e:
        print(f"  [manual] inbox.json is invalid JSON: {e}")
        return []
    out = []
    for e in entries:
        e.setdefault("source", "Curated")
        e.setdefault("category", "curated")
        out.append(e)
    print(f"  [manual] inbox: {len(out)} loops")
    return out

"""Build public/prompts.json for the AI Prompts page from data/prompts.csv.

Prompts are a curated, static library (unlike loops, they aren't scraped or
trending-scored), so this is a straight CSV -> JSON transform: parse the
`inside` checklist into a list and keep only published rows + useful fields.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "prompts.csv"
PUBLIC = Path(__file__).resolve().parent.parent / "public"

FIELDS = [
    "slug",
    "title",
    "model",
    "type",
    "tag",
    "plan",
    "description",
    "inside",
    "example",
    "framework",
    "framework_reason",
    "master_prompt",
]


def _inside(raw: str) -> list[str]:
    raw = (raw or "").strip()
    if not raw:
        return []
    try:
        val = json.loads(raw)
        return [str(x) for x in val] if isinstance(val, list) else [str(val)]
    except json.JSONDecodeError:
        return [raw]


def build() -> int:
    if not DATA.exists():
        print("  [prompts] no prompts.csv, skipping")
        return 0
    prompts = []
    with DATA.open(newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("is_published") or "t").strip().lower() in {"f", "false", "0"}:
                continue
            if not (row.get("title") or "").strip():
                continue
            p = {k: (row.get(k) or "").strip() for k in FIELDS}
            p["inside"] = _inside(row.get("inside", ""))
            prompts.append(p)

    prompts.sort(key=lambda p: (p["type"], p["title"].lower()))
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / "prompts.json").write_text(
        json.dumps(prompts, indent=2, ensure_ascii=False)
    )
    print(f"  [prompts] {len(prompts)} prompts -> {PUBLIC / 'prompts.json'}")
    return len(prompts)


if __name__ == "__main__":
    build()

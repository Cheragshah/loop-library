"""Canonical store for collected loops.

A "loop" is a reusable AI-agent prompt with a clear task and stopping condition.
Every collector emits dicts with the same shape; `merge` deduplicates them into
data/loops.json and maintains trending signals across runs.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
STORE_PATH = DATA_DIR / "loops.json"

# The columns every loop carries through the pipeline and into the exports.
FIELDS = [
    "id",
    "name",          # the name of the loop (what to call the command)
    "command",       # the complete loop prompt, ready to repurpose
    "what_it_does",  # one-line summary of the loop's job
    "category",
    "author",
    "source",        # human label, e.g. "Forward Future"
    "source_url",
    "tags",
    "votes",
    "mentions",      # how many sources/runs surfaced this loop -> trending signal
    "trending",      # computed score
    "first_seen",
    "last_seen",
    "published",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def normalize_id(name: str, command: str) -> str:
    """Stable id from the loop's identity, so the same loop dedupes across sources."""
    key = re.sub(r"\s+", " ", f"{name} {command}".strip().lower())
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def load() -> dict[str, dict]:
    if not STORE_PATH.exists():
        return {}
    return {l["id"]: l for l in json.loads(STORE_PATH.read_text())}


def _trending_score(loop: dict) -> float:
    """Cheap, transparent ranking: cross-source mentions + votes + recency."""
    mentions = loop.get("mentions", 1)
    votes = loop.get("votes", 0) or 0
    score = mentions * 3 + votes
    try:
        last = datetime.strptime(loop.get("last_seen", _now()), "%Y-%m-%d")
        age_days = (datetime.utcnow() - last).days
        score += max(0, 14 - age_days)  # recency bonus, fades over two weeks
    except ValueError:
        pass
    return round(score, 2)


def merge(existing: dict[str, dict], collected: list[dict]) -> dict[str, dict]:
    """Fold freshly collected loops into the store, updating trending signals."""
    today = _now()
    for raw in collected:
        name = (raw.get("name") or "").strip()
        command = (raw.get("command") or "").strip()
        if not name or not command:
            continue  # a loop without a name or a command can't be repurposed
        lid = normalize_id(name, command)
        prior = existing.get(lid)
        loop = {
            "id": lid,
            "name": name,
            "command": command,
            "what_it_does": (raw.get("what_it_does") or "").strip(),
            "category": (raw.get("category") or "uncategorized").strip().lower(),
            "author": (raw.get("author") or "").strip(),
            "source": raw.get("source", ""),
            "source_url": raw.get("source_url", ""),
            "tags": raw.get("tags", []),
            "votes": raw.get("votes", 0) or 0,
            "published": raw.get("published", ""),
        }
        if prior:
            sources = set(prior.get("_sources", [prior.get("source", "")]))
            sources.add(loop["source"])
            loop["mentions"] = len(sources)
            loop["_sources"] = sorted(s for s in sources if s)
            loop["first_seen"] = prior.get("first_seen", today)
            loop["votes"] = max(prior.get("votes", 0), loop["votes"])
        else:
            loop["mentions"] = 1
            loop["_sources"] = [loop["source"]] if loop["source"] else []
            loop["first_seen"] = today
        loop["last_seen"] = today
        loop["trending"] = _trending_score(loop)
        existing[lid] = loop
    return existing


def save(store: dict[str, dict]) -> list[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    loops = sorted(store.values(), key=lambda l: l.get("trending", 0), reverse=True)
    STORE_PATH.write_text(json.dumps(loops, indent=2, ensure_ascii=False))
    return loops

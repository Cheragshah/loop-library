"""Aggregate trending loops mentioned on Reddit, RSS feeds, and (optionally) X.

These sources are noisy: people post loops as free text, not structured rows.
We pull candidate posts and use a light heuristic to keep ones that actually
look like a repurposable loop (an imperative prompt with a stopping condition).
For higher-quality extraction, collect.py can run the AI refiner over results.
"""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET

import requests

HEADERS = {"User-Agent": "loop-library-collector/1.0 (+personal research)"}

# Subreddits + queries worth scanning for loop-style prompts.
REDDIT_QUERIES = [
    ("ClaudeAI", "loop prompt"),
    ("PromptEngineering", "agent loop"),
    ("ClaudeCode", "loop"),
]

# Newsletters / blogs that publish loops, exposed as RSS. Add your own.
RSS_FEEDS: list[str] = []

# Signals that a blob of text is actually a reusable loop, not just chatter.
_LOOP_HINT = re.compile(
    r"\b(loop|until|repeat|each (step|time)|stop(ping)? (when|condition)|verify|iterate)\b",
    re.IGNORECASE,
)
_IMPERATIVE = re.compile(r"^\s*(review|refactor|keep|whenever|search|run|generate|audit|"
                         r"check|build|update|write|find|continue|iterate|repeat)",
                         re.IGNORECASE)


def _looks_like_loop(text: str) -> bool:
    text = text.strip()
    return 40 <= len(text) <= 4000 and bool(_LOOP_HINT.search(text)) and bool(
        _IMPERATIVE.search(text)
    )


def _from_reddit() -> list[dict]:
    out = []
    for sub, query in REDDIT_QUERIES:
        url = f"https://www.reddit.com/r/{sub}/search.json"
        params = {"q": query, "restrict_sr": 1, "sort": "top", "t": "month", "limit": 25}
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=30)
            r.raise_for_status()
            posts = r.json().get("data", {}).get("children", [])
        except Exception as e:
            print(f"  [social] reddit r/{sub} skipped: {e}")
            continue
        for p in posts:
            d = p.get("data", {})
            body = (d.get("selftext") or "").strip()
            if not _looks_like_loop(body):
                continue
            out.append(
                {
                    "name": d.get("title", "").strip()[:120],
                    "command": body,
                    "what_it_does": d.get("title", "").strip(),
                    "category": "community",
                    "author": f"u/{d.get('author', '')}",
                    "source": f"Reddit r/{sub}",
                    "source_url": "https://www.reddit.com" + d.get("permalink", ""),
                    "votes": d.get("score", 0),
                    "tags": [sub.lower(), "reddit"],
                }
            )
    print(f"  [social] reddit: {len(out)} candidate loops")
    return out


def _from_rss() -> list[dict]:
    out = []
    for feed in RSS_FEEDS:
        try:
            r = requests.get(feed, headers=HEADERS, timeout=30)
            r.raise_for_status()
            root = ET.fromstring(r.content)
        except Exception as e:
            print(f"  [social] rss {feed} skipped: {e}")
            continue
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            desc = re.sub(r"<[^>]+>", "", item.findtext("description") or "").strip()
            if not _looks_like_loop(desc):
                continue
            out.append(
                {
                    "name": title[:120],
                    "command": desc,
                    "what_it_does": title,
                    "category": "newsletter",
                    "author": "",
                    "source": "RSS",
                    "source_url": (item.findtext("link") or "").strip(),
                    "tags": ["rss"],
                }
            )
    if RSS_FEEDS:
        print(f"  [social] rss: {len(out)} candidate loops")
    return out


def _from_x() -> list[dict]:
    """X/Twitter needs an API bearer token; without it we skip honestly."""
    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        print("  [social] X skipped: set X_BEARER_TOKEN to enable")
        return []
    out = []
    try:
        r = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            headers={"Authorization": f"Bearer {token}"},
            params={"query": '"loop" (prompt OR agent) -is:retweet lang:en', "max_results": 50},
            timeout=30,
        )
        r.raise_for_status()
        for t in r.json().get("data", []):
            body = t.get("text", "").strip()
            if not _looks_like_loop(body):
                continue
            out.append(
                {
                    "name": body[:80],
                    "command": body,
                    "what_it_does": body[:120],
                    "category": "community",
                    "author": "",
                    "source": "X",
                    "source_url": f"https://x.com/i/web/status/{t.get('id')}",
                    "tags": ["x"],
                }
            )
    except Exception as e:
        print(f"  [social] X failed: {e}")
    print(f"  [social] X: {len(out)} candidate loops")
    return out


def collect() -> list[dict]:
    return _from_reddit() + _from_rss() + _from_x()

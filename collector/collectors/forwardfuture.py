"""Scrape public loop libraries that use the Forward Future page markup.

The reference page renders every loop server-side as a `<tr class="loop-row">`
with clean data-attributes, so a dependency-free regex pass is reliable. Other
libraries sharing this template can be added to SITES.
"""

from __future__ import annotations

import html
import re

import requests

SITES = [
    {
        "name": "Forward Future",
        "url": "https://signals.forwardfuture.com/loop-library/",
        "base": "https://signals.forwardfuture.com/loop-library/",
    },
]

HEADERS = {"User-Agent": "loop-library-collector/1.0 (+personal research)"}

_ROW = re.compile(r'<tr\b[^>]*class="loop-row".*?</tr>', re.DOTALL)
_ATTR = lambda name: re.compile(rf'data-{name}="([^"]*)"')
_CATEGORY = re.compile(r'class="loop-category"[^>]*>(.*?)</span>', re.DOTALL)
_AUTHOR = re.compile(r'class="loop-attribution"[^>]*>(.*?)</span>', re.DOTALL)
_TITLE = re.compile(r'class="loop-title-link"\s+href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)
_SUMMARY = re.compile(r'class="loop-summary"[^>]*>(.*?)</p>', re.DOTALL)
_PROMPT = re.compile(r'<p[^>]*\bdata-prompt\b[^>]*>(.*?)</p>', re.DOTALL)
_VOTES = re.compile(r'data-vote-count[^>]*>(\d+)<')
_TAGS = _ATTR("search")


def _clean(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)          # drop nested tags
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def _abs_url(base: str, href: str) -> str:
    if href.startswith("http"):
        return href
    return base.rstrip("/") + "/" + href.lstrip("./")


def _parse_site(site: dict) -> list[dict]:
    resp = requests.get(site["url"], headers=HEADERS, timeout=30)
    resp.raise_for_status()
    loops = []
    for block in _ROW.findall(resp.text):
        title = _TITLE.search(block)
        prompt = _PROMPT.search(block)
        if not title or not prompt:
            continue
        href, name = title.group(1), _clean(title.group(2))
        author = _AUTHOR.search(block)
        author = re.sub(r"^By\s+", "", _clean(author.group(1))) if author else ""
        summary = _SUMMARY.search(block)
        votes = _VOTES.search(block)
        cat = _ATTR("category").search(block)
        pub = _ATTR("published").search(block)
        tags = _TAGS.search(block)
        loops.append(
            {
                "name": name,
                "command": _clean(prompt.group(1)),
                "what_it_does": _clean(summary.group(1)) if summary else "",
                "category": cat.group(1) if cat else "",
                "author": author,
                "source": site["name"],
                "source_url": _abs_url(site["base"], href),
                "published": pub.group(1) if pub else "",
                "votes": int(votes.group(1)) if votes else 0,
                "tags": tags.group(1).split() if tags else [],
            }
        )
    return loops


def collect() -> list[dict]:
    out = []
    for site in SITES:
        try:
            found = _parse_site(site)
            print(f"  [forwardfuture] {site['name']}: {len(found)} loops")
            out.extend(found)
        except Exception as e:  # one bad site shouldn't sink the run
            print(f"  [forwardfuture] {site['name']} FAILED: {e}")
    return out

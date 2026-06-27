"""Write a self-contained, offline dashboard: dist/dashboard/index.html.

The loop data is embedded directly into the page so it works by double-clicking
the file (no server, no CORS issues). Search, category filter, sort, and a
copy-to-clipboard button per loop mirror the reference site.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DASH = Path(__file__).resolve().parent / "dist" / "dashboard"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trending Loop Library</title>
<style>
  :root {{ --bg:#0b0f17; --card:#151b27; --line:#243043; --txt:#e7ecf3;
           --muted:#8b97a8; --accent:#5b8cff; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--txt);
          font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; }}
  header {{ padding:28px 24px 12px; }}
  h1 {{ margin:0 0 4px; font-size:22px; }}
  .sub {{ color:var(--muted); font-size:13px; }}
  .controls {{ display:flex; gap:10px; flex-wrap:wrap; padding:12px 24px 4px; }}
  input,select {{ background:var(--card); color:var(--txt); border:1px solid var(--line);
                  border-radius:8px; padding:9px 12px; font-size:14px; }}
  #q {{ flex:1; min-width:220px; }}
  .filters {{ display:flex; gap:8px; flex-wrap:wrap; padding:10px 24px; }}
  .chip {{ background:var(--card); border:1px solid var(--line); color:var(--muted);
           padding:5px 12px; border-radius:999px; cursor:pointer; font-size:13px; }}
  .chip.on {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  .grid {{ display:grid; gap:14px; padding:14px 24px 60px;
           grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
           padding:16px; display:flex; flex-direction:column; gap:8px; }}
  .meta {{ display:flex; justify-content:space-between; align-items:center;
           color:var(--muted); font-size:12px; }}
  .cat {{ text-transform:capitalize; color:var(--accent); }}
  .name {{ font-size:16px; font-weight:600; margin:0; }}
  .does {{ color:var(--muted); font-size:13px; margin:0; }}
  pre {{ background:#0c121d; border:1px solid var(--line); border-radius:8px;
         padding:10px; white-space:pre-wrap; font-size:12.5px; max-height:170px;
         overflow:auto; margin:0; }}
  .row {{ display:flex; justify-content:space-between; align-items:center; gap:8px; }}
  button.copy {{ background:var(--accent); color:#fff; border:0; border-radius:8px;
                 padding:7px 12px; cursor:pointer; font-size:13px; }}
  .badge {{ font-size:11px; color:var(--muted); }}
  a {{ color:var(--accent); }}
</style>
</head>
<body>
<header>
  <h1>🔁 Trending Loop Library</h1>
  <div class="sub">{count} loops · updated {updated} · sources: {sources}</div>
</header>
<div class="controls">
  <input id="q" placeholder="Search loops, authors, keywords…">
  <select id="sort">
    <option value="trending">Sort: Trending</option>
    <option value="votes">Sort: Votes</option>
    <option value="name">Sort: A–Z</option>
    <option value="last_seen">Sort: Newest</option>
  </select>
</div>
<div class="filters" id="filters"></div>
<div class="grid" id="grid"></div>
<script>
const LOOPS = {data};
const grid = document.getElementById('grid');
const q = document.getElementById('q');
const sortSel = document.getElementById('sort');
let activeCat = 'all';

const cats = ['all', ...Array.from(new Set(LOOPS.map(l => l.category))).sort()];
const filters = document.getElementById('filters');
cats.forEach(c => {{
  const el = document.createElement('span');
  el.className = 'chip' + (c === 'all' ? ' on' : '');
  el.textContent = c;
  el.onclick = () => {{ activeCat = c;
    document.querySelectorAll('.chip').forEach(x => x.classList.remove('on'));
    el.classList.add('on'); render(); }};
  filters.appendChild(el);
}});

function esc(s) {{ return (s||'').replace(/[&<>]/g, m => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[m])); }}

function render() {{
  const term = q.value.toLowerCase();
  const key = sortSel.value;
  let rows = LOOPS.filter(l =>
    (activeCat === 'all' || l.category === activeCat) &&
    (!term || (l.name+' '+l.command+' '+l.what_it_does+' '+l.author+' '+(l.tags||[]).join(' ')).toLowerCase().includes(term)));
  rows.sort((a,b) => key === 'name' ? a.name.localeCompare(b.name)
                    : (b[key] > a[key] ? 1 : b[key] < a[key] ? -1 : 0));
  grid.innerHTML = rows.map(l => `
    <div class="card">
      <div class="meta"><span class="cat">${{esc(l.category)}}</span>
        <span>★ ${{l.trending}} · ▲ ${{l.votes||0}}</span></div>
      <p class="name">${{esc(l.name)}}</p>
      <p class="does">${{esc(l.what_it_does)}}</p>
      <pre>${{esc(l.command)}}</pre>
      <div class="row">
        <span class="badge">${{esc(l.author||'—')}} · ${{esc(l.source)}}
          ${{l.source_url ? `· <a href="${{l.source_url}}" target="_blank">link</a>` : ''}}</span>
        <button class="copy" data-cmd="${{esc(l.command)}}">Copy loop</button>
      </div>
    </div>`).join('') || '<p style="color:var(--muted);padding:20px">No loops match.</p>';
  grid.querySelectorAll('button.copy').forEach(b =>
    b.onclick = () => {{ navigator.clipboard.writeText(b.dataset.cmd);
      b.textContent = 'Copied ✓'; setTimeout(() => b.textContent = 'Copy loop', 1200); }});
}}
q.oninput = render; sortSel.onchange = render; render();
</script>
</body>
</html>
"""


def export(loops: list[dict]) -> Path:
    DASH.mkdir(parents=True, exist_ok=True)
    public = [{k: v for k, v in l.items() if not k.startswith("_")} for l in loops]
    sources = sorted({l["source"] for l in loops if l.get("source")})
    html = TEMPLATE.format(
        count=len(loops),
        updated=datetime.now().strftime("%Y-%m-%d %H:%M"),
        sources=", ".join(sources) or "—",
        data=json.dumps(public, ensure_ascii=False),
    )
    out = DASH / "index.html"
    out.write_text(html, encoding="utf-8")
    return out

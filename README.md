# 🔁 Trending Loop Library

A self-updating **React + TypeScript** app cataloging trending **loops** —
reusable AI-agent prompts with a clear task and a stopping condition. Inspired by
the [Forward Future Loop Library](https://signals.forwardfuture.com/loop-library/).

Each loop carries the three fields you need to repurpose it:

| Field | Meaning |
|-------|---------|
| **Loop name** | What to call the loop / command |
| **Complete loop (command)** | The full prompt, copy-paste ready |
| **What it does** | One-line job, so you know how to reuse it |

…plus category, author, source, votes, a **trending** score, and dates.

## Architecture

```
GitHub Actions (daily cron)
  └─ python3 collector/collect.py     # scrape + aggregate + curate
       └─ writes public/loops.json    # committed back to the repo
            └─ Vite builds src/*.tsx into a static site
                 └─ deployed to GitHub Pages (free, no server)
```

The Python collectors are unchanged and run in CI; the front end is a static
React app that simply fetches `public/loops.json`.

## Local development

```bash
npm install
npm run collect     # runs the Python collectors -> public/loops.json + xlsx
npm run dev         # http://localhost:5173/loop-library/
npm run build       # static site -> dist/
```

`npm run collect` needs Python 3 with `requests` + `openpyxl`
(`pip install requests openpyxl`).

## Project layout

```
loop-library/
├─ src/                     React + TS app
│  ├─ App.tsx               search / filter / sort / category chips
│  ├─ components/LoopCard.tsx
│  ├─ useLoops.ts           fetches public/loops.json
│  └─ types.ts
├─ public/
│  ├─ loops.json            data the app reads (committed by CI)
│  └─ loop-library.xlsx     downloadable Excel export
├─ collector/              Python data pipeline
│  ├─ collect.py            orchestrator
│  ├─ store.py              dedupe + trending score + canonical store
│  ├─ collectors/           forwardfuture / social / manual
│  └─ data/                 canonical loops.json + inbox.json (your curated loops)
└─ .github/workflows/deploy.yml   cron refresh + build + Pages deploy
```

## Sources (collectors)

| Collector | Status | Notes |
|-----------|--------|-------|
| `forwardfuture` | ✅ automatic | Scrapes the Forward Future loop library (70+ loops). Add more sites with the same markup in `collector/collectors/forwardfuture.py → SITES`. |
| `social` (Reddit) | ⚠️ needs creds | Reddit blocks unauthenticated scraping (403). Plug in Reddit OAuth for reliability. |
| `social` (RSS) | ✅ opt-in | Add feeds to `RSS_FEEDS`. |
| `social` (X) | ⚠️ opt-in | Set `X_BEARER_TOKEN`. |
| `manual` | ✅ always | Hand-curated loops in `collector/data/inbox.json`. |

## Deploy to GitHub Pages

1. Create a repo (e.g. `loop-library`) and push this folder:
   ```bash
   cd loop-library
   git init && git add . && git commit -m "feat: trending loop library"
   git branch -M main
   git remote add origin https://github.com/<you>/loop-library.git
   git push -u origin main
   ```
2. In the repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. The workflow builds + deploys on every push and daily at 06:00 UTC. Trigger a
   manual refresh anytime from the **Actions** tab → *Refresh loops & deploy* →
   *Run workflow*.
4. Live at `https://<you>.github.io/loop-library/`.

> The Vite `base` is `/loop-library/` (set in `vite.config.ts`). If you deploy to
> a custom domain or a `<you>.github.io` user site, set `BASE_PATH=/` — CI already
> passes the repo name automatically.

## How "trending" is scored

`mentions × 3 + votes + recency bonus`, where *mentions* counts how many sources
surfaced the same loop (deduped by name + command). Tune it in
`collector/store.py → _trending_score`.

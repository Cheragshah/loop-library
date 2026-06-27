import { useMemo, useState } from "react";
import { LoopCard } from "./components/LoopCard";
import { useLoops } from "./useLoops";
import type { SortKey } from "./types";

const SORTS: { key: SortKey; label: string }[] = [
  { key: "trending", label: "Trending" },
  { key: "votes", label: "Votes" },
  { key: "name", label: "A–Z" },
  { key: "last_seen", label: "Newest" },
];

export default function App() {
  const { loops, loading, error } = useLoops();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [sort, setSort] = useState<SortKey>("trending");

  const categories = useMemo(
    () => ["all", ...Array.from(new Set(loops.map((l) => l.category))).sort()],
    [loops],
  );

  const sources = useMemo(
    () => Array.from(new Set(loops.map((l) => l.source).filter(Boolean))),
    [loops],
  );

  const visible = useMemo(() => {
    const q = query.toLowerCase();
    return loops
      .filter((l) => category === "all" || l.category === category)
      .filter(
        (l) =>
          !q ||
          `${l.name} ${l.command} ${l.what_it_does} ${l.author} ${(
            l.tags ?? []
          ).join(" ")}`
            .toLowerCase()
            .includes(q),
      )
      .sort((a, b) =>
        sort === "name"
          ? a.name.localeCompare(b.name)
          : (b[sort] as number) - (a[sort] as number) ||
            String(b[sort]).localeCompare(String(a[sort])),
      );
  }, [loops, query, category, sort]);

  return (
    <div className="app">
      <header className="hero">
        <h1>🔁 Trending Loop Library</h1>
        <p className="sub">
          {loops.length} reusable AI-agent loops · sources:{" "}
          {sources.join(", ") || "—"} ·{" "}
          <a href={`${import.meta.env.BASE_URL}loop-library.xlsx`}>
            download Excel
          </a>
        </p>
      </header>

      <div className="controls">
        <input
          className="search"
          placeholder="Search loops, authors, keywords…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          className="sort"
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
        >
          {SORTS.map((s) => (
            <option key={s.key} value={s.key}>
              Sort: {s.label}
            </option>
          ))}
        </select>
      </div>

      <div className="chips">
        {categories.map((c) => (
          <button
            key={c}
            className={`chip ${c === category ? "on" : ""}`}
            onClick={() => setCategory(c)}
          >
            {c}
          </button>
        ))}
      </div>

      {loading && <p className="note">Loading loops…</p>}
      {error && (
        <p className="note error">
          Couldn’t load loops.json ({error}). Run{" "}
          <code>npm run collect</code> first.
        </p>
      )}

      {!loading && !error && (
        <main className="grid">
          {visible.length ? (
            visible.map((l) => <LoopCard key={l.id} loop={l} />)
          ) : (
            <p className="note">No loops match your filters.</p>
          )}
        </main>
      )}

      <footer className="foot">
        Auto-updated daily via GitHub Actions · inspired by Forward Future’s Loop
        Library
      </footer>
    </div>
  );
}

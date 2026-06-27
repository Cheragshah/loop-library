import { useMemo, useState } from "react";
import { PromptCard } from "../components/PromptCard";
import { usePrompts } from "../usePrompts";

/** Distinct, sorted values for a field, used to build filter dropdowns. */
function uniq(values: string[]): string[] {
  return Array.from(new Set(values.filter(Boolean))).sort();
}

export function PromptsPage() {
  const { prompts, loading, error } = usePrompts();
  const [query, setQuery] = useState("");
  const [type, setType] = useState("all");
  const [model, setModel] = useState("all");
  const [plan, setPlan] = useState("all");

  const types = useMemo(() => uniq(prompts.map((p) => p.type)), [prompts]);
  const models = useMemo(() => uniq(prompts.map((p) => p.model)), [prompts]);
  const plans = useMemo(() => uniq(prompts.map((p) => p.plan)), [prompts]);

  const visible = useMemo(() => {
    const q = query.toLowerCase();
    return prompts
      .filter((p) => type === "all" || p.type === type)
      .filter((p) => model === "all" || p.model === model)
      .filter((p) => plan === "all" || p.plan === plan)
      .filter(
        (p) =>
          !q ||
          `${p.title} ${p.description} ${p.tag} ${p.model} ${p.framework} ${p.master_prompt}`
            .toLowerCase()
            .includes(q),
      );
  }, [prompts, query, type, model, plan]);

  return (
    <>
      <header className="hero">
        <h1>✨ AI Prompt Library</h1>
        <p className="sub">
          {prompts.length} production-ready prompts for ChatGPT, Claude, Gemini &
          more
        </p>
      </header>

      <div className="controls">
        <input
          className="search"
          placeholder="Search prompts, tags, models…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select className="sort" value={type} onChange={(e) => setType(e.target.value)}>
          <option value="all">Type: All</option>
          {types.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <select className="sort" value={model} onChange={(e) => setModel(e.target.value)}>
          <option value="all">Model: All</option>
          {models.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <select className="sort" value={plan} onChange={(e) => setPlan(e.target.value)}>
          <option value="all">Plan: All</option>
          {plans.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </div>

      {loading && <p className="note">Loading prompts…</p>}
      {error && (
        <p className="note error">
          Couldn’t load prompts.json ({error}). Run <code>npm run collect</code>{" "}
          first.
        </p>
      )}

      {!loading && !error && (
        <>
          <p className="result-count">{visible.length} prompts</p>
          <main className="grid">
            {visible.length ? (
              visible.map((p) => <PromptCard key={p.slug} prompt={p} />)
            ) : (
              <p className="note">No prompts match your filters.</p>
            )}
          </main>
        </>
      )}
    </>
  );
}

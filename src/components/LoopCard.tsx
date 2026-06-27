import { useState } from "react";
import type { Loop } from "../types";

export function LoopCard({ loop }: { loop: Loop }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(loop.command);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <article className="card">
      <div className="card-meta">
        <span className="cat">{loop.category}</span>
        <span className="stats" title="trending score · votes">
          ★ {loop.trending} · ▲ {loop.votes ?? 0}
        </span>
      </div>

      <h3 className="card-name">{loop.name}</h3>
      {loop.slash && <code className="card-slash">{loop.slash}</code>}
      <p className="card-does">{loop.what_it_does}</p>

      <pre className="card-command">{loop.command}</pre>

      <div className="card-foot">
        <span className="byline">
          {loop.author || "—"} · {loop.source}
          {loop.source_url && (
            <>
              {" · "}
              <a href={loop.source_url} target="_blank" rel="noreferrer">
                link
              </a>
            </>
          )}
        </span>
        <button className="copy-btn" onClick={copy}>
          {copied ? "Copied ✓" : "Copy loop"}
        </button>
      </div>
    </article>
  );
}

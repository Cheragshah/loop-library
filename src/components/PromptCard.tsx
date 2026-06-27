import { useState } from "react";
import type { Prompt } from "../types";

export function PromptCard({ prompt }: { prompt: Prompt }) {
  const [copied, setCopied] = useState(false);
  const [open, setOpen] = useState(false);

  const copy = async () => {
    await navigator.clipboard.writeText(prompt.master_prompt);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <article className="card">
      <div className="card-meta">
        <span className="cat">{prompt.type}</span>
        {prompt.plan && <span className={`plan plan-${prompt.plan.replace(/\s+/g, "-").toLowerCase()}`}>{prompt.plan}</span>}
      </div>

      <h3 className="card-name">{prompt.title}</h3>

      <div className="badges">
        {prompt.model && <span className="badge-pill">{prompt.model}</span>}
        {prompt.tag && <span className="badge-pill">{prompt.tag}</span>}
        {prompt.framework && (
          <span className="badge-pill" title={prompt.framework_reason}>
            {prompt.framework}
          </span>
        )}
      </div>

      <p className="card-does">{prompt.description}</p>

      {prompt.inside.length > 0 && (
        <ul className="inside">
          {prompt.inside.map((i, n) => (
            <li key={n}>{i}</li>
          ))}
        </ul>
      )}

      <button className="reveal" onClick={() => setOpen((o) => !o)}>
        {open ? "Hide prompt ▲" : "Show prompt ▼"}
      </button>
      {open && <pre className="card-command">{prompt.master_prompt}</pre>}

      {open && prompt.example && (
        <p className="example">
          <strong>Example:</strong> {prompt.example}
        </p>
      )}

      <div className="card-foot">
        <span className="byline">{prompt.model}</span>
        <button className="copy-btn" onClick={copy}>
          {copied ? "Copied ✓" : "Copy prompt"}
        </button>
      </div>
    </article>
  );
}

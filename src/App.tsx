import { useEffect, useState } from "react";
import { LoopsPage } from "./pages/LoopsPage";
import { PromptsPage } from "./pages/PromptsPage";

type Route = "loops" | "prompts";

function currentRoute(): Route {
  return window.location.hash.replace("#/", "") === "prompts"
    ? "prompts"
    : "loops";
}

export default function App() {
  const [route, setRoute] = useState<Route>(currentRoute());

  useEffect(() => {
    const onHash = () => setRoute(currentRoute());
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  return (
    <div className="app">
      <nav className="nav">
        <span className="brand">Signal Library</span>
        <div className="tabs">
          <a className={`tab ${route === "loops" ? "on" : ""}`} href="#/loops">
            🔁 Loops
          </a>
          <a
            className={`tab ${route === "prompts" ? "on" : ""}`}
            href="#/prompts"
          >
            ✨ AI Prompts
          </a>
        </div>
      </nav>

      {route === "prompts" ? <PromptsPage /> : <LoopsPage />}

      <footer className="foot">
        Auto-updated via GitHub Actions · loops inspired by Forward Future
      </footer>
    </div>
  );
}

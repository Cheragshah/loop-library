import { useEffect, useState } from "react";
import type { Prompt } from "./types";

interface PromptsState {
  prompts: Prompt[];
  loading: boolean;
  error: string | null;
}

/** Loads the curated prompt library from public/prompts.json. */
export function usePrompts(): PromptsState {
  const [state, setState] = useState<PromptsState>({
    prompts: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    const url = `${import.meta.env.BASE_URL}prompts.json`;
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status} loading ${url}`);
        return r.json();
      })
      .then((prompts: Prompt[]) =>
        setState({ prompts, loading: false, error: null }),
      )
      .catch((e: Error) =>
        setState({ prompts: [], loading: false, error: e.message }),
      );
  }, []);

  return state;
}

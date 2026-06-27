import { useEffect, useState } from "react";
import type { Loop } from "./types";

interface LoopsState {
  loops: Loop[];
  loading: boolean;
  error: string | null;
}

/** Loads the committed catalog from public/loops.json (respecting Vite's base). */
export function useLoops(): LoopsState {
  const [state, setState] = useState<LoopsState>({
    loops: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    const url = `${import.meta.env.BASE_URL}loops.json`;
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status} loading ${url}`);
        return r.json();
      })
      .then((loops: Loop[]) =>
        setState({ loops, loading: false, error: null }),
      )
      .catch((e: Error) =>
        setState({ loops: [], loading: false, error: e.message }),
      );
  }, []);

  return state;
}

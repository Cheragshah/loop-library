import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Default to root "/" so host-at-root deploys (Vercel, custom domains) work.
// The GitHub Pages workflow sets BASE_PATH=/<repo>/ to serve from a subpath.
const base = process.env.BASE_PATH ?? "/";

export default defineConfig({
  base,
  plugins: [react()],
});

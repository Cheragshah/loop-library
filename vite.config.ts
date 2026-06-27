import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// For GitHub Pages project sites the app is served from /<repo>/.
// Override by setting BASE_PATH (e.g. "/" for a custom domain or user site).
const base = process.env.BASE_PATH ?? "/loop-library/";

export default defineConfig({
  base,
  plugins: [react()],
});

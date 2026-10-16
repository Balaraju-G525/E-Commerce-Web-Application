import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// /api requests are proxied to Django, so cookies/CSRF work on one origin
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { "/api": "http://127.0.0.1:8000" } },
});

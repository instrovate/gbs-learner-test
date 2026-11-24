import { defineConfig } from "vite"; import react from "@vitejs/plugin-react";
// Sends /ask to your API on port 8000, so the web app works in a browser workspace too.
export default defineConfig({ plugins: [react()], server: { proxy: { "/ask": "http://localhost:8000" } } });

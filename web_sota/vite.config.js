import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: { "@": path.resolve(__dirname, "./src") },
    },
    server: {
        port: 10747,
        host: "127.0.0.1",
        proxy: {
            "/api": { target: "http://127.0.0.1:10746", changeOrigin: true },
            "/health": { target: "http://127.0.0.1:10746", changeOrigin: true },
        },
    },
});

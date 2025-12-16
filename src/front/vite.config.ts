import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
    root: ".",
    plugins: [tailwindcss()],
    server: {
        host: true,
        allowedHosts: true,
        port: 5173,
    }
});

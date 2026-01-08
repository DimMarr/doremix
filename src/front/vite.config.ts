import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
    root: ".",
    plugins: [tailwindcss()],
    resolve: {
        alias: {
            "@models": path.resolve(__dirname, "./models"),
            "@components": path.resolve(__dirname, "./components"),
            "@utils": path.resolve(__dirname, "./utils"),
            "@services": path.resolve(__dirname, "./services"),
            "@hooks": path.resolve(__dirname, "./hooks"),
            "@pages": path.resolve(__dirname, "./pages"),
            "@styles": path.resolve(__dirname, "./styles"),
            "@assets": path.resolve(__dirname, "./assets"),
            "@config": path.resolve(__dirname, "./config"),
            "@repositories": path.resolve(__dirname, "./repositories"),
            "@store": path.resolve(__dirname, "./store"),
            "@layouts": path.resolve(__dirname, "./layouts"),
        },
    },
    server: {
        host: true,
        allowedHosts: true,
        port: 5173,
    }
});

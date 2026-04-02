import { defineConfig } from "vitest/config";
import { resolve } from "path";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
    test: {
        environment: "jsdom",
        globals: true,
    },
    resolve: {
        alias: {
            "@models": resolve(__dirname, "./models"),
            "@components": resolve(__dirname, "./components"),
            "@utils": resolve(__dirname, "./utils"),
            "@services": resolve(__dirname, "./services"),
            "@hooks": resolve(__dirname, "./hooks"),
            "@pages": resolve(__dirname, "./pages"),
            "@styles": resolve(__dirname, "./styles"),
            "@assets": resolve(__dirname, "./assets"),
            "@config": resolve(__dirname, "./config"),
            "@repositories": resolve(__dirname, "./repositories"),
            "@store": resolve(__dirname, "./store"),
            "@layouts": resolve(__dirname, "./layouts"),
        },
    },
});

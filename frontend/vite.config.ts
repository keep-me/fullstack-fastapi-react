import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  base: "./",
  esbuild: {
    treeShaking: true,
    minifyIdentifiers: true,
    pure: ["console.log", "console.info", "console.warn"],
  },
  build: {
    target: "esnext",
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom", "react-router-dom"],
          ui: ["@chakra-ui/react", "@emotion/react", "react-icons"],
          utils: [
            "@reduxjs/toolkit",
            "react-redux",
            "react-hook-form",
            "axios",
            "jwt-decode",
            "@fingerprintjs/fingerprintjs",
          ],
        },
      },
    },
    chunkSizeWarningLimit: 500,
    minify: "terser",
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
});

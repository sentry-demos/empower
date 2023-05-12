import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";
import { sentryVitePlugin } from "@sentry/vite-plugin";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), vueJsx(), sentryVitePlugin({
    sourcemaps: {
        assets: "./dist/**",
    },
    org: 'testorg-az',
    project: 'vue',
    authToken: process.env.VITE_SENTRY_AUTH_TOKEN,
  })],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    sourcemap: true,
  },
});

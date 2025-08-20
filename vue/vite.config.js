import { sentryVitePlugin } from "@sentry/vite-plugin";
import { fileURLToPath, URL } from "url";

import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import vueJsx from "@vitejs/plugin-vue-jsx";


// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    server: {
      headers: {
        'Document-Policy': 'js-profiling'
      }
    },
    plugins: [vue(), vueJsx(), sentryVitePlugin({
      org: env.SENTRY_ORG,
      project: env.VUE_SENTRY_PROJECT,
      authToken: env.VITE_RELEASE_TOKEN
    })],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    build: {
      sourcemap: true
    }
  }
});
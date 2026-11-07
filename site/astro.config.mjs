// Edgar Mendonca's portfolio: https://edgar-mendonca.github.io/Edgar-Mendonca/
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://edgar-mendonca.github.io",
  base: "/Edgar-Mendonca",
  trailingSlash: "ignore",
  build: { inlineStylesheets: "always" },
});

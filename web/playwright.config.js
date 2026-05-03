import { defineConfig } from "@playwright/test"
import { resolve } from "path"

export default defineConfig({
  testDir: "./e2e",

  timeout: 10_000,
  expect: {
    timeout: 10_000
  },

  use: {
    baseURL: "http://localhost:8080/",
    headless: true,
  },

  projects: [
    {
      name: "chromium",
      use: {
        browserName: "chromium"
      }
    },
  ],

  webServer: {
    command: "python3 -m http.server 8080",
    url: "http://localhost:8080/",

    cwd: resolve(import.meta.dirname, ".."),

    reuseExistingServer: !process.env.CI,

    timeout: 10_000,
  },
})

import { test, expect } from "@playwright/test"

test("app loads and Pyodide initialises", async ({ page }) => {
  await page.goto("/web/")

  const startGameBtn = page.getByRole("button", { name: "Iniciar jogo" })

  await expect(startGameBtn).toBeVisible()
})

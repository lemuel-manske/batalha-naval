import { describe, it, expect } from "vitest"
import { readFileSync, readdirSync } from "fs"
import { resolve, join } from "path"

const ROOT = resolve(import.meta.dirname, "../..")
const WORKER_SRC = readFileSync(resolve(import.meta.dirname, "../src/worker.js"), "utf-8")

function extractModuleList(src) {
  const match = src.match(/const modules = \[([\s\S]*?)\]/)
  if (!match) throw new Error("Could not find modules array in worker.js")
  return [...match[1].matchAll(/"([^"]+)"/g)].map(m => m[1])
}

function getPyModules(dir, prefix = "") {
  const entries = readdirSync(join(ROOT, "batalha_naval", dir), { withFileTypes: true })
  const result = []
  for (const e of entries) {
    if (e.name === "__pycache__") continue
    if (e.isDirectory()) {
      result.push(...getPyModules(join(dir, e.name), prefix))
    } else if (e.name.endsWith(".py")) {
      const mod = join(dir, e.name.replace(/\.py$/, ""))
      result.push(mod.replace(/\\/g, "/"))
    }
  }
  return result
}

describe("worker.js module list", () => {
  it("lists every .py file in batalha_naval/", () => {
    const listed = new Set(extractModuleList(WORKER_SRC))
    const actual = getPyModules("")

    const missing = actual.filter(m => !listed.has(m))
    expect(missing, `Missing from worker.js modules list: ${missing.join(", ")}`).toEqual([])
  })
})

# E2E Tests Design — 2026-05-02

## Context

Batalha Naval is a browser-based Battleship game. The game engine runs in Python via Pyodide (WebAssembly) inside a Web Worker. The frontend is plain JavaScript. There are already unit tests (pytest for Python, Vitest for JS), but no end-to-end tests that exercise the full browser stack.

## Goals

Cover the critical happy paths:
- The app loads and Pyodide initialises without errors
- A Human vs AI game can be played to completion
- An AI vs AI game can be played to completion

## Framework

**Playwright** — chosen for its async-aware assertions (`waitForSelector`, `expect(locator).toBeVisible()`), generous configurable timeouts, and clean GitHub Actions integration. Chromium only in CI for speed.

## File Layout

```
web/
  playwright.config.js     # Playwright configuration
  e2e/
    game.spec.js           # E2E test file
  package.json             # playwright added as devDependency
```

`web/vitest.config.js` already exists; Playwright uses its own config file and does not conflict.

## Server Setup

Playwright's `webServer` config starts `python3 -m http.server 8080` from the **repo root** (not `web/`). This is required so that:
- `web/index.html` is served at `http://localhost:8080/web/`
- `batalha_naval/*.py` (copied into `web/batalha_naval/` by `make build-web`) are accessible to the worker's relative-URL fetches

`baseURL` is set to `http://localhost:8080/web/`.

## Test Cases

### 1. App loads (smoke test)
- Navigate to `/`
- Wait for `#loading-indicator` to have class `hidden` (Pyodide ready), timeout 60 s
- Assert `#btn-start` is enabled
- Assert `#board-player` and `#board-enemy` are visible

### 2. HvAI game plays to completion
- Navigate to `/`
- Wait for Pyodide ready
- Select strategy "Aleatória" (random) from `#select-strategy-hvai`
- Click `#btn-shuffle` to randomise ship placement
- Click `#btn-start`
- In a loop (max 100 iterations): click a non-attacked cell on `#board-enemy`; after each click wait for `EVT_STATE` to process (wait for cell to gain `.hit` or `.miss` class); if `#end-banner` is visible, break
- Assert `#end-banner` is visible and `#end-message` is non-empty

### 3. AIvAI game plays to completion
- Navigate to `/`
- Wait for Pyodide ready
- Click `#btn-aivai` to switch mode
- Select strategy "Aleatória" for both `#select-strategy-p1` and `#select-strategy-p2`
- Click both shuffle buttons (`.btn-shuffle-side`)
- Click `#btn-start`
- Poll `#end-banner` visibility, timeout 120 s (AI takes multiple turns automatically)
- Assert `#end-banner` is visible and `#end-message` is non-empty

## Makefile

```makefile
test-e2e:
	npx playwright test --project=chromium
	working-directory: web  # or via --config flag
```

Or: `npm run test:e2e --prefix web` with a `test:e2e` script in `web/package.json`.

## CI — `.github/workflows/test.yml`

New `e2e` job:

```yaml
e2e:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version-file: web/.nvmrc
    - run: npm ci
      working-directory: web
    - run: npx playwright install --with-deps chromium
      working-directory: web
    - uses: actions/setup-python@v5
      with:
        python-version: "3.x"
    - run: make build-web
    - run: make test-e2e
```

`make build-web` copies `batalha_naval/` into `web/batalha_naval/` so the HTTP server can serve the Python files.

## Constraints

- Pyodide init can take 10–30 s; all tests use a 60 s timeout for the ready signal
- AIvAI test uses a 120 s timeout since the AI plays all turns automatically
- Only "random" strategy is used in E2E tests to avoid MCTS think time making tests slow/flaky
- `web/batalha_naval/` is gitignored; `make build-web` must run before E2E tests (handled in CI by the explicit step)

import { uiState } from "../src/state.js"
import { toggleDir, initPlacementHandlers } from "../src/placement.js"

let sharedEngine

beforeAll(() => {
  sharedEngine = {
    canPlaceShip: vi.fn(),
    placeShip: vi.fn(),
    randomPlacement: vi.fn(),
    clearPlacement: vi.fn(),
  }

  initPlacementHandlers(sharedEngine)
})

beforeEach(() => {
  vi.clearAllMocks()

  uiState.mode = "hvai"
  uiState.phase = "placement"
  uiState.drag = { ship: null, cell: null }
  uiState.players.player1.currentDir = "h"
  uiState.players.player2.currentDir = "h"
})

test("toggleDir switches player1 direction from h to v", () => {
  toggleDir("player1", sharedEngine)

  expect(uiState.players.player1.currentDir).toBe("v")
})

test("toggleDir switches player1 direction from v back to h", () => {
  uiState.players.player1.currentDir = "v"

  toggleDir("player1", sharedEngine)

  expect(uiState.players.player1.currentDir).toBe("h")
})

test("toggleDir updates rotate button text to reflect new direction", () => {
  toggleDir("player1", sharedEngine)

  expect(document.getElementById("btn-rotate").textContent).toContain("Vertical")
})

test("toggleDir updates the dragging ship dir when ship belongs to that player", () => {
  uiState.drag.ship = { name: "destroyer", dir: "h", player: "player1" }

  toggleDir("player1", sharedEngine)

  expect(uiState.drag.ship.dir).toBe("v")
})

test("toggleDir does not change drag ship dir when ship belongs to a different player", () => {
  uiState.drag.ship = { name: "destroyer", dir: "h", player: "player2" }

  toggleDir("player1", sharedEngine)

  expect(uiState.drag.ship.dir).toBe("h")
})

test("toggleDir calls canPlaceShip when ship is actively dragging over a cell", () => {
  uiState.drag.ship = { name: "destroyer", dir: "h", player: "player1" }
  uiState.drag.cell = { row: 2, col: 3 }

  toggleDir("player1", sharedEngine)

  expect(sharedEngine.canPlaceShip).toHaveBeenCalledWith("destroyer", 2, 3, "v", "player1")
})

test("toggleDir does not call canPlaceShip when no cell is hovered", () => {
  uiState.drag.ship = { name: "destroyer", dir: "h", player: "player1" }
  uiState.drag.cell = null

  toggleDir("player1", sharedEngine)

  expect(sharedEngine.canPlaceShip).not.toHaveBeenCalled()
})

test("btn-shuffle click calls engine.randomPlacement for player1", () => {
  document.getElementById("btn-shuffle").click()

  expect(sharedEngine.randomPlacement).toHaveBeenCalledWith("player1")
})

test("btn-clear click calls engine.clearPlacement for player1", () => {
  document.getElementById("btn-clear").click()

  expect(sharedEngine.clearPlacement).toHaveBeenCalledWith("player1")
})

test("btn-rotate click toggles player1 direction", () => {
  document.getElementById("btn-rotate").click()

  expect(uiState.players.player1.currentDir).toBe("v")
})

import { uiState } from "../src/state.js"
import { elBoardPlayer, elBoardEnemy } from "../src/ui.js"
import {
  renderEmptyBoards, renderBoard, renderPlacementBoard,
  renderPlacementShipList, renderPlacementPreview, clearPlacementPreview,
} from "../src/render.js"
import { BOARD_SIZE } from "../src/constants.js"

function emptyBoard() {
  return Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(null))
}

beforeEach(() => {
  uiState.mode = "hvai"
  uiState.players.player1 = { pendingShips: [], placedShips: [], placementBoard: null, currentDir: "h" }
  uiState.players.player2 = { pendingShips: [], placedShips: [], placementBoard: null, currentDir: "h" }

  renderEmptyBoards()
})

test("renderEmptyBoards creates 100 cells in each board", () => {
  expect(elBoardPlayer.querySelectorAll(".cell").length).toBe(100)
  expect(elBoardEnemy.querySelectorAll(".cell").length).toBe(100)
})

test("renderBoard marks attacked ship cell as hit", () => {
  const board = emptyBoard()
  board[0][0] = "destroyer"

  renderBoard(elBoardPlayer, board, [[0, 0]], true, false, null)

  const cell = elBoardPlayer.querySelectorAll(".cell")[0]
  expect(cell.classList.contains("hit")).toBe(true)
})

test("renderBoard marks attacked empty cell as miss", () => {
  renderBoard(elBoardPlayer, emptyBoard(), [[1, 1]], false, false, null)

  const cell = elBoardPlayer.querySelectorAll(".cell")[1 * BOARD_SIZE + 1]
  expect(cell.classList.contains("miss")).toBe(true)
})

test("renderBoard shows ship when showShips is true", () => {
  const board = emptyBoard()
  board[2][3] = "carrier"

  renderBoard(elBoardPlayer, board, [], true, false, null)

  const cell = elBoardPlayer.querySelectorAll(".cell")[2 * BOARD_SIZE + 3]
  expect(cell.classList.contains("ship")).toBe(true)
  expect(cell.classList.contains("ship-carrier")).toBe(true)
})

test("renderBoard hides ship when showShips is false", () => {
  const board = emptyBoard()
  board[2][3] = "carrier"

  renderBoard(elBoardPlayer, board, [], false, false, null)

  const cell = elBoardPlayer.querySelectorAll(".cell")[2 * BOARD_SIZE + 3]
  expect(cell.classList.contains("ship")).toBe(false)
})

test("renderBoard marks cells clickable and fires onAttack with correct coord", () => {
  const onAttack = vi.fn()

  renderBoard(elBoardPlayer, emptyBoard(), [], false, true, onAttack)

  const cell = elBoardPlayer.querySelectorAll(".cell")[0]
  expect(cell.classList.contains("clickable")).toBe(true)

  cell.click()

  expect(onAttack).toHaveBeenCalledWith([0, 0])
})

test("renderBoard clicking a cell removes all clickable classes", () => {
  renderBoard(elBoardPlayer, emptyBoard(), [], false, true, vi.fn())

  elBoardPlayer.querySelectorAll(".cell")[0].click()

  expect(elBoardPlayer.querySelectorAll(".clickable").length).toBe(0)
})

test("renderBoard does not mark already-attacked cell as clickable", () => {
  renderBoard(elBoardPlayer, emptyBoard(), [[0, 0]], false, true, vi.fn())

  const cell = elBoardPlayer.querySelectorAll(".cell")[0]
  expect(cell.classList.contains("clickable")).toBe(false)
})

test("renderPlacementBoard renders 100 cells with data attributes", () => {
  uiState.players.player1.placementBoard = emptyBoard()

  renderPlacementBoard("player1")

  const cells = elBoardPlayer.querySelectorAll(".cell")
  expect(cells.length).toBe(100)
  expect(cells[0].dataset.row).toBe("0")
  expect(cells[0].dataset.col).toBe("0")
  expect(cells[0].dataset.player).toBe("player1")
})

test("renderPlacementBoard marks placed ship cells with ship class", () => {
  const board = emptyBoard()
  board[3][4] = "submarine"
  uiState.players.player1.placementBoard = board

  renderPlacementBoard("player1")

  const cell = elBoardPlayer.querySelectorAll(".cell")[3 * BOARD_SIZE + 4]
  expect(cell.classList.contains("ship-submarine")).toBe(true)
})

test("renderPlacementShipList renders pending as draggable and placed as .placed", () => {
  uiState.players.player1.pendingShips = ["destroyer"]
  uiState.players.player1.placedShips = ["carrier"]

  renderPlacementShipList("player1")

  const items = document.getElementById("ship-list").querySelectorAll("li")
  expect(items.length).toBe(2)
  expect(items[0].style.cursor).toBe("grab")
  expect(items[1].classList.contains("placed")).toBe(true)
})

test("renderPlacementPreview applies preview-valid class", () => {
  uiState.players.player1.placementBoard = emptyBoard()
  renderPlacementBoard("player1")

  renderPlacementPreview("player1", [[0, 0], [0, 1]], true)

  const cells = elBoardPlayer.querySelectorAll(".cell")
  expect(cells[0].classList.contains("preview-valid")).toBe(true)
  expect(cells[1].classList.contains("preview-valid")).toBe(true)
  expect(cells[2].classList.contains("preview-valid")).toBe(false)
})

test("renderPlacementPreview applies preview-invalid class when invalid", () => {
  uiState.players.player1.placementBoard = emptyBoard()
  renderPlacementBoard("player1")

  renderPlacementPreview("player1", [[0, 0]], false)

  expect(elBoardPlayer.querySelectorAll(".cell")[0].classList.contains("preview-invalid")).toBe(true)
})

test("clearPlacementPreview removes preview-valid and preview-invalid", () => {
  uiState.players.player1.placementBoard = emptyBoard()
  renderPlacementBoard("player1")
  renderPlacementPreview("player1", [[0, 0]], true)

  clearPlacementPreview("player1")

  expect(elBoardPlayer.querySelectorAll(".cell")[0].classList.contains("preview-valid")).toBe(false)
})

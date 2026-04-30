import { uiState } from "../src/state.js"
import {
  elBtnStart, elBtnCancel, elBtnRestart, elBtnHvai, elBtnAivai,
  elPlacement, elPlacementAivai, elEndBanner, elStatus,
  setPhase, setMode, updateStartButton, endGame, cancelGame,
} from "../src/ui.js"

beforeEach(() => {
  uiState.phase = "idle"
  uiState.mode = "hvai"
  uiState.gameState = null
  uiState.aiScheduled = false

  for (const ps of Object.values(uiState.players)) {
    ps.pendingShips = []
    ps.placedShips = []
    ps.placementBoard = null
    ps.currentDir = "h"
  }
})

test("setPhase idle shows start button and hides cancel and restart", () => {
  setPhase("idle")

  expect(elBtnStart.classList.contains("hidden")).toBe(false)
  expect(elBtnCancel.classList.contains("hidden")).toBe(true)
  expect(elBtnRestart.classList.contains("hidden")).toBe(true)
})

test("setPhase placement shows start and cancel, hides restart", () => {
  setPhase("placement")

  expect(elBtnStart.classList.contains("hidden")).toBe(false)
  expect(elBtnCancel.classList.contains("hidden")).toBe(false)
  expect(elBtnRestart.classList.contains("hidden")).toBe(true)
})

test("setPhase placement shows hvai placement area", () => {
  uiState.mode = "hvai"

  setPhase("placement")

  expect(elPlacement.classList.contains("hidden")).toBe(false)
  expect(elPlacementAivai.classList.contains("hidden")).toBe(true)
})

test("setPhase placement shows aivai placement area when mode is aivai", () => {
  uiState.mode = "aivai"

  setPhase("placement")

  expect(elPlacementAivai.classList.contains("hidden")).toBe(false)
  expect(elPlacement.classList.contains("hidden")).toBe(true)
})

test("setPhase game shows cancel only, hides start and restart", () => {
  setPhase("game")

  expect(elBtnCancel.classList.contains("hidden")).toBe(false)
  expect(elBtnStart.classList.contains("hidden")).toBe(true)
  expect(elBtnRestart.classList.contains("hidden")).toBe(true)
})

test("setPhase end shows restart button and end banner", () => {
  setPhase("end")

  expect(elBtnRestart.classList.contains("hidden")).toBe(false)
  expect(elEndBanner.classList.contains("hidden")).toBe(false)
})

test("setPhase idle hides status bar", () => {
  setPhase("idle")

  expect(elStatus.classList.contains("hidden")).toBe(true)
})

test("setPhase game shows status bar", () => {
  setPhase("game")

  expect(elStatus.classList.contains("hidden")).toBe(false)
})

test("setPhase end hides end banner after transitioning back to idle", () => {
  setPhase("end")
  setPhase("idle")

  expect(elEndBanner.classList.contains("hidden")).toBe(true)
})

test("setMode hvai marks hvai button active and aivai inactive", () => {
  setMode("hvai")

  expect(elBtnHvai.classList.contains("active")).toBe(true)
  expect(elBtnAivai.classList.contains("active")).toBe(false)
})

test("setMode aivai marks aivai button active and hvai inactive", () => {
  setMode("aivai")

  expect(elBtnAivai.classList.contains("active")).toBe(true)
  expect(elBtnHvai.classList.contains("active")).toBe(false)
})

test("updateStartButton disables start when player1 has pending ships in hvai", () => {
  uiState.phase = "placement"
  uiState.mode = "hvai"
  uiState.players.player1.pendingShips = ["carrier"]

  updateStartButton()

  expect(elBtnStart.disabled).toBe(true)
})

test("updateStartButton enables start when player1 has no pending ships in hvai", () => {
  uiState.phase = "placement"
  uiState.mode = "hvai"
  uiState.players.player1.pendingShips = []

  updateStartButton()

  expect(elBtnStart.disabled).toBe(false)
})

test("updateStartButton disables start in aivai when player2 still has pending ships", () => {
  uiState.phase = "placement"
  uiState.mode = "aivai"
  uiState.players.player1.pendingShips = []
  uiState.players.player2.pendingShips = ["carrier"]

  updateStartButton()

  expect(elBtnStart.disabled).toBe(true)
})

test("updateStartButton enables start in aivai when both sides are fully placed", () => {
  uiState.phase = "placement"
  uiState.mode = "aivai"
  uiState.players.player1.pendingShips = []
  uiState.players.player2.pendingShips = []

  updateStartButton()

  expect(elBtnStart.disabled).toBe(false)
})

test("endGame sets player1 win message in hvai mode", () => {
  uiState.mode = "hvai"

  endGame("player1")

  expect(document.getElementById("end-message").textContent).toBe("Você venceu!")
})

test("endGame sets player2 win message in hvai mode", () => {
  uiState.mode = "hvai"

  endGame("player2")

  expect(document.getElementById("end-message").textContent).toBe("IA venceu!")
})

test("cancelGame resets gameState to null", () => {
  uiState.gameState = { current_turn: "player1" }

  cancelGame()

  expect(uiState.gameState).toBeNull()
})

test("cancelGame sets phase back to idle", () => {
  uiState.phase = "game"

  cancelGame()

  expect(uiState.phase).toBe("idle")
})

test("cancelGame clears placed and pending ships for both players", () => {
  uiState.players.player1.pendingShips = ["carrier"]
  uiState.players.player2.placedShips = ["destroyer"]

  cancelGame()

  expect(uiState.players.player1.pendingShips).toEqual([])
  expect(uiState.players.player2.placedShips).toEqual([])
})

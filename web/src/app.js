import { AI_TURN_DELAY_MS, AIVAI_TURN_DELAY_MS, MODE_CONFIG } from "./constants.js"
import { uiState } from "./state.js"
import {
  renderEmptyBoards, renderGame, renderPlacementBoard,
  renderPlacementShipList, renderPlacementPreview,
} from "./render.js"
import {
  setPhase, setMode, endGame, cancelGame, updateStartButton,
  elBtnStart, elBtnCancel, elBtnRestart, elBtnHvai, elBtnAivai,
  elStatus, elLoading, hide,
  elSelectStrategyHvai, elSelectStrategyP1, elSelectStrategyP2,
} from "./ui.js"
import { initPlacementHandlers } from "./placement.js"
import { createEngine } from "./engine.js"

const engine = createEngine({
  onReady() {
    renderEmptyBoards()
    setPhase("idle")
    hide(elLoading)
  },

  onPlacementState(player, { pending, placed, board }) {
    const ps = uiState.players[player]
    ps.pendingShips = pending
    ps.placedShips = placed
    ps.placementBoard = board
    renderPlacementShipList(player)
    renderPlacementBoard(player)
    updateStartButton()
  },

  onPlacementValid(player, cells, valid) {
    renderPlacementPreview(player, cells, valid)
  },

  onGameState(state, mode) {
    uiState.gameState = state
    if (uiState.phase !== "game") setPhase("game")
    renderGame((coord) => engine.attack(coord))
    if (state.winner) {
      endGame(state.winner)
      return
    }
    if (mode === "aivai" || (!mode && uiState.mode === "aivai")) {
      scheduleAiVsAi()
    } else if (state.current_turn === "player2" && uiState.mode === "hvai") {
      scheduleAiTurn()
    }
  },

  onError(message) {
    console.error("Worker error:", message)
    elStatus.textContent = "Erro interno — veja o console."
  },
})

function scheduleAiTurn() {
  setTimeout(() => {
    if (uiState.gameState && !uiState.gameState.winner)
      engine.aiTurn()
  }, AI_TURN_DELAY_MS)
}

function scheduleAiVsAi() {
  if (uiState.aiScheduled) return
  uiState.aiScheduled = true
  setTimeout(() => {
    uiState.aiScheduled = false
    if (uiState.gameState && !uiState.gameState.winner) {
      engine.aiTurn()
    }
  }, AIVAI_TURN_DELAY_MS)
}

elBtnHvai.onclick = () => setMode("hvai")
elBtnAivai.onclick = () => setMode("aivai")

elSelectStrategyHvai.onchange = () => { uiState.strategy.hvai     = elSelectStrategyHvai.value }
elSelectStrategyP1.onchange   = () => { uiState.strategy.p1_aivai = elSelectStrategyP1.value }
elSelectStrategyP2.onchange   = () => { uiState.strategy.p2_aivai = elSelectStrategyP2.value }

elBtnStart.onclick = () => {
  if (uiState.phase === "idle") {
    setPhase("placement")
    elStatus.textContent = MODE_CONFIG[uiState.mode].statusPlacement
    engine.init(uiState.mode)
  } else if (uiState.phase === "placement") {
    engine.startGame(uiState.mode, uiState.strategy)
  }
}

elBtnCancel.onclick = () => { cancelGame(); renderEmptyBoards() }
elBtnRestart.onclick = () => { cancelGame(); renderEmptyBoards() }

initPlacementHandlers(engine)

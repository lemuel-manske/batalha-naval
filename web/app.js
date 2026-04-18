import {
  AI_TURN_DELAY_MS,
  AIVAI_TURN_DELAY_MS,
  MODE_CONFIG,
} from "./constants.js";
import { uiState } from "./state.js";
import {
  renderEmptyBoards,
  renderGame,
  renderPlacementBoard,
  renderPlacementShipList,
  renderPlacementPreview,
} from "./render.js";
import {
  setPhase,
  setMode,
  endGame,
  cancelGame,
  updateStartButton,
  elBtnStart,
  elBtnCancel,
  elBtnRestart,
  elBtnHvai,
  elBtnAivai,
  elStatus,
  elLoading,
  hide,
} from "./ui.js";
import { initPlacementHandlers } from "./placement.js";

const worker = new Worker("worker.js");

function scheduleAiTurn() {
  setTimeout(() => {
    if (uiState.gameState && !uiState.gameState.winner) {
      worker.postMessage({ type: "ai_turn" });
    }
  }, AI_TURN_DELAY_MS);
}

function scheduleAiVsAi() {
  if (uiState.aiScheduled) return;
  uiState.aiScheduled = true;
  setTimeout(() => {
    uiState.aiScheduled = false;
    if (uiState.gameState && !uiState.gameState.winner) {
      worker.postMessage({ type: "ai_turn" });
    }
  }, AIVAI_TURN_DELAY_MS);
}

worker.onmessage = function (e) {
  const msg = e.data;

  if (msg.type === "ready") {
    renderEmptyBoards();
    setPhase("idle");
    hide(elLoading);
  } else if (msg.type === "placement_state") {
    const player = msg.player ?? "player1";
    const ps = uiState.players[player];
    ps.pendingShips = msg.pending;
    ps.placedShips = msg.placed;
    ps.placementBoard = msg.board ?? null;
    renderPlacementShipList(player);
    renderPlacementBoard(player);
    updateStartButton();
  } else if (msg.type === "placement_valid") {
    renderPlacementPreview(msg.player ?? "player1", msg.cells, msg.valid);
  } else if (msg.type === "state") {
    uiState.gameState = msg.state;
    if (uiState.phase !== "game") setPhase("game");
    renderGame((coord) => worker.postMessage({ type: "attack", coord }));
    if (msg.state.winner) {
      endGame(msg.state.winner);
      return;
    }
    if (msg.mode === "aivai" || (!msg.mode && uiState.mode === "aivai")) {
      scheduleAiVsAi();
    } else if (
      msg.state.current_turn === "player2" &&
      uiState.mode === "hvai"
    ) {
      scheduleAiTurn();
    }
  } else if (msg.type === "error") {
    console.error("Worker error:", msg.message);
    elStatus.textContent = "Erro interno — veja o console.";
  }
};

elBtnHvai.onclick = () => setMode("hvai");
elBtnAivai.onclick = () => setMode("aivai");

elBtnStart.onclick = () => {
  if (uiState.phase === "idle") {
    setPhase("placement");
    elStatus.textContent = MODE_CONFIG[uiState.mode].statusPlacement;
    worker.postMessage({ type: "init", mode: uiState.mode });
  } else if (uiState.phase === "placement") {
    worker.postMessage({ type: "start_game", mode: uiState.mode });
  }
};

elBtnCancel.onclick = () => {
  cancelGame();
  renderEmptyBoards();
};

elBtnRestart.onclick = () => {
  cancelGame();
  renderEmptyBoards();
};

initPlacementHandlers(worker);

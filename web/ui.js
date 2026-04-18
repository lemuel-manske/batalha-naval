import { uiState } from "./state.js";
import { MODE_CONFIG } from "./constants.js";

const $ = (id) => document.getElementById(id);

export const elLoading = $("loading-indicator");
export const elStatus = $("game-status");
export const elEndBanner = $("end-banner");
export const elEndMsg = $("end-message");
export const elPlacement = $("placement-area");
export const elPlacementAivai = $("placement-area-aivai");
export const elBoardPlayer = $("board-player");
export const elBoardEnemy = $("board-enemy");
export const elBtnStart = $("btn-start");
export const elBtnCancel = $("btn-cancel");
export const elBtnRestart = $("btn-restart");
export const elBtnHvai = $("btn-hvai");
export const elBtnAivai = $("btn-aivai");
export const elLabelPlayer = $("label-player");
export const elLabelEnemy = $("label-enemy");

export function show(el) {
  el.classList.remove("hidden");
}

export function hide(el) {
  el.classList.add("hidden");
}

export function setPlaceholder(board, on) {
  board.classList.toggle("placeholder", on);
}

function bothSidesComplete() {
  return (
    uiState.players.player1.pendingShips.length === 0 &&
    uiState.players.player2.pendingShips.length === 0
  );
}

export function updateStartButton() {
  if (uiState.phase !== "placement") return;
  if (uiState.mode === "aivai") {
    elBtnStart.disabled = !bothSidesComplete();
  } else {
    elBtnStart.disabled = uiState.players.player1.pendingShips.length > 0;
  }
}

export function setPhase(phase) {
  uiState.phase = phase;

  const inGame = phase === "game" || phase === "end";
  elBtnHvai.disabled = inGame;
  elBtnAivai.disabled = inGame;

  hide(elBtnStart);
  hide(elBtnCancel);
  hide(elBtnRestart);
  hide(elPlacement);
  hide(elPlacementAivai);

  if (phase === "idle") {
    show(elBtnStart);
    elBtnStart.disabled = false;
  } else if (phase === "placement") {
    show(elBtnStart);
    elBtnStart.disabled = true;
    if (uiState.mode === "aivai") {
      show(elPlacementAivai);
    } else {
      show(elPlacement);
    }
    show(elBtnCancel);
  } else if (phase === "game") {
    show(elBtnCancel);
  } else if (phase === "end") {
    show(elBtnRestart);
  }

  if (phase === "idle" || phase === "loading") {
    hide(elStatus);
  } else {
    show(elStatus);
  }

  if (phase === "end") {
    show(elEndBanner);
  } else {
    hide(elEndBanner);
  }

  const isPlaceholderPlayer = phase === "idle" || phase === "loading";
  const isPlaceholderEnemy = isPlaceholderPlayer || phase === "placement";
  setPlaceholder(elBoardPlayer, isPlaceholderPlayer);
  setPlaceholder(elBoardEnemy, isPlaceholderEnemy);

  const cfg = MODE_CONFIG[uiState.mode];
  if (phase === "placement" && uiState.mode === "aivai") {
    setPlaceholder(elBoardEnemy, false);
    elLabelPlayer.textContent = cfg.labelPlayer;
    elLabelEnemy.textContent = cfg.labelEnemy;
  } else if (phase !== "game" && phase !== "end") {
    elLabelPlayer.textContent = cfg.labelPlayer;
    elLabelEnemy.textContent = cfg.labelEnemy;
  }
}

export function setMode(mode) {
  uiState.mode = mode;
  elBtnHvai.classList.toggle("active", mode === "hvai");
  elBtnAivai.classList.toggle("active", mode === "aivai");
  const cfg = MODE_CONFIG[mode];
  elLabelPlayer.textContent = cfg.labelPlayer;
  elLabelEnemy.textContent = cfg.labelEnemy;
}

export function endGame(winner) {
  const cfg = MODE_CONFIG[uiState.mode];
  elEndMsg.textContent = winner === "player1" ? cfg.winPlayer1 : cfg.winPlayer2;
  setPhase("end");
}

export function cancelGame() {
  uiState.gameState = null;
  uiState.aiScheduled = false;
  for (const ps of Object.values(uiState.players)) {
    ps.pendingShips = [];
    ps.placedShips = [];
    ps.placementBoard = null;
  }
  setPhase("idle");
  hide(elStatus);
}

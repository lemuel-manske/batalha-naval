const BOARD_SIZE = 10;
const AI_TURN_DELAY_MS = 300;
const AIVAI_TURN_DELAY_MS = 600;

const worker = new Worker("worker.js");

const uiState = {
  phase: "loading",
  mode: "hvai",

  // player1 placement
  pendingShips: [],
  placedShips: [],
  placementBoard: null,

  // player2 placement (aivai)
  pendingShips2: [],
  placedShips2: [],
  placementBoard2: null,

  // drag
  dragShip: null, // { name, dir, player }
  dragCell: null, // { row, col }
  dragPlayer: null, // "player1" | "player2"

  // dirs independentes por jogador
  currentDir1: "h",
  currentDir2: "h",

  gameState: null,
};

const $ = (id) => document.getElementById(id);

const elLoading = $("loading-indicator");
const elStatus = $("game-status");
const elEndBanner = $("end-banner");
const elEndMsg = $("end-message");
const elPlacement = $("placement-area");
const elPlacementAivai = $("placement-area-aivai");
const elBoardPlayer = $("board-player");
const elBoardEnemy = $("board-enemy");
const elBtnStart = $("btn-start");
const elBtnCancel = $("btn-cancel");
const elBtnRestart = $("btn-restart");
const elBtnHvai = $("btn-hvai");
const elBtnAivai = $("btn-aivai");
const elLabelPlayer = $("label-player");
const elLabelEnemy = $("label-enemy");

function show(el) {
  el.classList.remove("hidden");
}
function hide(el) {
  el.classList.add("hidden");
}
function setPlaceholder(board, on) {
  board.classList.toggle("placeholder", on);
}

function bothSidesComplete() {
  return (
    uiState.pendingShips.length === 0 && uiState.pendingShips2.length === 0
  );
}

function setPhase(phase) {
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
    if (uiState.mode === "aivai") {
      elBtnStart.disabled = !bothSidesComplete();
      show(elPlacementAivai);
    } else {
      elBtnStart.disabled = uiState.pendingShips.length > 0;
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

  if (phase === "placement" && uiState.mode === "aivai") {
    setPlaceholder(elBoardEnemy, false);
    elLabelPlayer.textContent = "IA 1";
    elLabelEnemy.textContent = "IA 2";
  } else if (phase !== "game" && phase !== "end") {
    elLabelPlayer.textContent =
      uiState.mode === "hvai" ? "Seu tabuleiro" : "IA 1";
    elLabelEnemy.textContent =
      uiState.mode === "hvai" ? "Tabuleiro inimigo" : "IA 2";
  }
}

worker.onmessage = function (e) {
  const msg = e.data;

  if (msg.type === "ready") {
    renderEmptyBoards();
    setPhase("idle");
    hide(elLoading);
  } else if (msg.type === "placement_state") {
    const player = msg.player || "player1";
    if (player === "player2") {
      uiState.pendingShips2 = msg.pending;
      uiState.placedShips2 = msg.placed;
      uiState.placementBoard2 = msg.board || null;
      renderPlacementShipList("player2");
      renderPlacementBoard("player2");
    } else {
      uiState.pendingShips = msg.pending;
      uiState.placedShips = msg.placed;
      uiState.placementBoard = msg.board || null;
      renderPlacementShipList("player1");
      renderPlacementBoard("player1");
    }
    if (uiState.phase === "placement") {
      if (uiState.mode === "aivai") {
        elBtnStart.disabled = !bothSidesComplete();
      } else {
        elBtnStart.disabled = uiState.pendingShips.length > 0;
      }
    }
  } else if (msg.type === "placement_valid") {
    const player = msg.player || "player1";
    renderPlacementPreview(player, msg.cells, msg.valid);
  } else if (msg.type === "state") {
    uiState.gameState = msg.state;
    if (uiState.phase !== "game") setPhase("game");
    renderGame();
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

function setMode(mode) {
  uiState.mode = mode;
  elBtnHvai.classList.toggle("active", mode === "hvai");
  elBtnAivai.classList.toggle("active", mode === "aivai");
  elLabelPlayer.textContent = mode === "hvai" ? "Seu tabuleiro" : "IA 1";
  elLabelEnemy.textContent = mode === "hvai" ? "Tabuleiro inimigo" : "IA 2";
}

elBtnStart.onclick = () => {
  if (uiState.phase === "idle") {
    setPhase("placement");
    if (uiState.mode === "hvai") {
      elStatus.textContent = "Posicione seus navios e clique em Iniciar jogo.";
    } else {
      elStatus.textContent =
        "Posicione os navios de ambas as IAs e clique em Iniciar jogo.";
    }
    worker.postMessage({ type: "init", mode: uiState.mode });
  } else if (uiState.phase === "placement") {
    worker.postMessage({ type: "start_game", mode: uiState.mode });
  }
};

elBtnCancel.onclick = () => cancelGame();
elBtnRestart.onclick = () => cancelGame();

function cancelGame() {
  uiState.gameState = null;
  uiState.pendingShips = [];
  uiState.placedShips = [];
  uiState.placementBoard = null;
  uiState.pendingShips2 = [];
  uiState.placedShips2 = [];
  uiState.placementBoard2 = null;
  aiVsAiRunning = false;
  renderEmptyBoards();
  setPhase("idle");
  hide(elStatus);
}

function renderEmptyBoards() {
  [elBoardPlayer, elBoardEnemy].forEach((container) => {
    container.innerHTML = "";
    for (let i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      container.appendChild(cell);
    }
  });
}

function renderGame() {
  const state = uiState.gameState;
  const isHvai = uiState.mode === "hvai";

  renderBoard(
    elBoardPlayer,
    state.boards.player1,
    state.attacks.player2,
    true,
    false,
  );
  renderBoard(
    elBoardEnemy,
    state.boards.player2,
    state.attacks.player1,
    !isHvai,
    isHvai && state.current_turn === "player1" && !state.winner,
  );

  if (!state.winner) {
    if (isHvai) {
      elStatus.textContent =
        state.current_turn === "player1"
          ? "Sua vez — clique no tabuleiro inimigo"
          : "IA pensando...";
    } else {
      elStatus.textContent = `Turno: ${state.current_turn === "player1" ? "IA 1" : "IA 2"}`;
    }
  }
}

function renderBoard(container, board, attacks, showShips, clickable) {
  container.innerHTML = "";
  const attackSet = new Set(attacks.map(([r, c]) => `${r},${c}`));

  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      const key = `${r},${c}`;
      const attacked = attackSet.has(key);
      const shipName = board[r][c];

      if (attacked && shipName) {
        cell.classList.add("hit");
      } else if (attacked) {
        cell.classList.add("miss");
      } else if (showShips && shipName) {
        cell.classList.add("ship", `ship-${shipName}`);
      }

      if (clickable && !attacked) {
        cell.classList.add("clickable");
        cell.onclick = () => {
          container.querySelectorAll(".cell").forEach((el) => {
            el.classList.remove("clickable");
            el.onclick = null;
          });
          worker.postMessage({ type: "attack", coord: [r, c] });
        };
      }

      container.appendChild(cell);
    }
  }
}

function endGame(winner) {
  const isHvai = uiState.mode === "hvai";
  elEndMsg.textContent =
    winner === "player1"
      ? isHvai
        ? "Você venceu!"
        : "IA 1 venceu!"
      : isHvai
        ? "IA venceu!"
        : "IA 2 venceu!";
  setPhase("end");
}

function scheduleAiTurn() {
  setTimeout(() => {
    if (uiState.gameState && !uiState.gameState.winner) {
      worker.postMessage({ type: "ai_turn" });
    }
  }, AI_TURN_DELAY_MS);
}

let aiVsAiRunning = false;
function scheduleAiVsAi() {
  if (aiVsAiRunning) return;
  aiVsAiRunning = true;
  setTimeout(() => {
    aiVsAiRunning = false;
    if (uiState.gameState && !uiState.gameState.winner) {
      worker.postMessage({ type: "ai_turn" });
    }
  }, AIVAI_TURN_DELAY_MS);
}

const SHIP_LABELS = {
  carrier: "Porta-aviões (5)",
  battleship: "Encouraçado (4)",
  cruiser: "Cruzador (3)",
  submarine: "Submarino (3)",
  destroyer: "Destroyer (2)",
};

function renderPlacementShipList(player) {
  const listId =
    player === "player2"
      ? "ship-list-2"
      : uiState.mode === "aivai"
        ? "ship-list-1"
        : "ship-list";
  const list = $(listId);
  if (!list) return;
  list.innerHTML = "";

  const pending =
    player === "player2" ? uiState.pendingShips2 : uiState.pendingShips;
  const placed =
    player === "player2" ? uiState.placedShips2 : uiState.placedShips;

  for (const ship of pending) {
    const li = document.createElement("li");
    li.textContent = SHIP_LABELS[ship];
    li.dataset.ship = ship;
    li.dataset.player = player;
    li.style.cursor = "grab";
    li.onpointerdown = (e) => {
      e.preventDefault();
      const dir =
        player === "player2" ? uiState.currentDir2 : uiState.currentDir1;
      uiState.dragShip = { name: ship, dir, player };
      uiState.dragPlayer = player;
      li.classList.add("dragging");
    };
    list.appendChild(li);
  }

  for (const ship of placed) {
    const li = document.createElement("li");
    li.textContent = SHIP_LABELS[ship];
    li.className = "placed";
    list.appendChild(li);
  }
}

function _boardContainerFor(player) {
  return player === "player2" ? elBoardEnemy : elBoardPlayer;
}

function renderPlacementBoard(player) {
  const container = _boardContainerFor(player);
  container.innerHTML = "";
  const board =
    player === "player2" ? uiState.placementBoard2 : uiState.placementBoard;

  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.row = r;
      cell.dataset.col = c;
      cell.dataset.player = player;
      if (board && board[r][c]) {
        const shipName = board[r][c];
        cell.classList.add("ship", `ship-${shipName}`);
      }
      container.appendChild(cell);
    }
  }
}

function clearPlacementPreview(player) {
  const container = _boardContainerFor(player);
  container
    .querySelectorAll(".cell")
    .forEach((el) => el.classList.remove("preview-valid", "preview-invalid"));
}

function renderPlacementPreview(player, previewCells, previewValid) {
  clearPlacementPreview(player);
  if (!previewCells || previewCells.length === 0) return;
  const previewSet = new Set(previewCells.map(([r, c]) => `${r * 10 + c}`));
  _boardContainerFor(player)
    .querySelectorAll(".cell")
    .forEach((el, idx) => {
      if (previewSet.has(`${idx}`)) {
        el.classList.add(previewValid ? "preview-valid" : "preview-invalid");
      }
    });
}

function _validatePreviewAt(r, c) {
  if (!uiState.dragShip) return;
  worker.postMessage({
    type: "validate_placement",
    ship: uiState.dragShip.name,
    row: r,
    col: c,
    dir: uiState.dragShip.dir,
    player: uiState.dragShip.player,
  });
}

document.addEventListener("pointermove", (e) => {
  if (!uiState.dragShip) return;

  const el = document.elementFromPoint(e.clientX, e.clientY);
  const cell = el?.closest?.("[data-row]");

  if (cell) {
    const cellPlayer = cell.dataset.player;
    if (cellPlayer && cellPlayer !== uiState.dragShip.player) return;

    const r = +cell.dataset.row;
    const c = +cell.dataset.col;

    if (
      !uiState.dragCell ||
      uiState.dragCell.row !== r ||
      uiState.dragCell.col !== c
    ) {
      uiState.dragCell = { row: r, col: c };
      _validatePreviewAt(r, c);
    }
  } else {
    if (uiState.dragCell) {
      uiState.dragCell = null;
      clearPlacementPreview(uiState.dragShip.player);
    }
  }
});

document.addEventListener("pointerup", () => {
  if (!uiState.dragShip) return;

  if (uiState.dragCell) {
    worker.postMessage({
      type: "place_ship",
      ship: uiState.dragShip.name,
      row: uiState.dragCell.row,
      col: uiState.dragCell.col,
      dir: uiState.dragShip.dir,
      player: uiState.dragShip.player,
    });
  }

  document
    .querySelectorAll(".dragging")
    .forEach((el) => el.classList.remove("dragging"));
  const prevPlayer = uiState.dragShip.player;
  uiState.dragShip = null;
  uiState.dragCell = null;
  uiState.dragPlayer = null;
  clearPlacementPreview(prevPlayer);
});

document.addEventListener("keydown", (e) => {
  if ((e.key === "r" || e.key === "R") && uiState.phase === "placement") {
    if (uiState.dragShip) {
      toggleDir(uiState.dragShip.player);
    } else {
      toggleDir("player1");
    }
  }
});

function toggleDir(player) {
  if (player === "player2") {
    uiState.currentDir2 = uiState.currentDir2 === "h" ? "v" : "h";
    if (uiState.dragShip?.player === "player2")
      uiState.dragShip.dir = uiState.currentDir2;
    const btn = document.querySelector(
      ".btn-rotate-side[data-player='player2']",
    );
    if (btn)
      btn.textContent = `↕ Rotacionar (R) — ${uiState.currentDir2 === "h" ? "Horizontal" : "Vertical"}`;
    if (uiState.dragShip?.player === "player2" && uiState.dragCell) {
      _validatePreviewAt(uiState.dragCell.row, uiState.dragCell.col);
    }
  } else {
    uiState.currentDir1 = uiState.currentDir1 === "h" ? "v" : "h";
    if (uiState.dragShip?.player !== "player2")
      uiState.dragShip && (uiState.dragShip.dir = uiState.currentDir1);
    const btn =
      uiState.mode === "aivai"
        ? document.querySelector(".btn-rotate-side[data-player='player1']")
        : $("btn-rotate");
    if (btn)
      btn.textContent = `↕ Rotacionar (R) — ${uiState.currentDir1 === "h" ? "Horizontal" : "Vertical"}`;
    if (uiState.dragShip?.player !== "player2" && uiState.dragCell) {
      _validatePreviewAt(uiState.dragCell.row, uiState.dragCell.col);
    }
  }
}

$("btn-rotate").onclick = () => toggleDir("player1");
$("btn-shuffle").onclick = () =>
  worker.postMessage({ type: "random_placement", player: "player1" });
$("btn-clear").onclick = () =>
  worker.postMessage({ type: "clear_placement", player: "player1" });

document.querySelectorAll(".btn-rotate-side").forEach((btn) => {
  btn.onclick = () => toggleDir(btn.dataset.player);
});
document.querySelectorAll(".btn-shuffle-side").forEach((btn) => {
  btn.onclick = () =>
    worker.postMessage({
      type: "random_placement",
      player: btn.dataset.player,
    });
});
document.querySelectorAll(".btn-clear-side").forEach((btn) => {
  btn.onclick = () =>
    worker.postMessage({ type: "clear_placement", player: btn.dataset.player });
});

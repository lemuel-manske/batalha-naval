import { BOARD_SIZE, SHIP_LABELS, MODE_CONFIG } from "./constants.js";
import { uiState } from "./state.js";
import { elBoardPlayer, elBoardEnemy, elStatus } from "./ui.js";

export function boardContainerFor(player) {
  return player === "player2" ? elBoardEnemy : elBoardPlayer;
}

export function renderEmptyBoards() {
  for (const container of [elBoardPlayer, elBoardEnemy]) {
    container.innerHTML = "";
    for (let i = 0; i < BOARD_SIZE * BOARD_SIZE; i++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      container.appendChild(cell);
    }
  }
}

export function renderGame(onAttack) {
  const state = uiState.gameState;
  const isHvai = uiState.mode === "hvai";

  renderBoard(
    elBoardPlayer,
    state.boards.player1,
    state.attacks.player2,
    true,
    false,
    null,
  );
  renderBoard(
    elBoardEnemy,
    state.boards.player2,
    state.attacks.player1,
    !isHvai,
    isHvai && state.current_turn === "player1" && !state.winner,
    onAttack,
  );

  if (!state.winner) {
    const cfg = MODE_CONFIG[uiState.mode];
    elStatus.textContent =
      state.current_turn === "player1"
        ? cfg.statusTurnPlayer1
        : cfg.statusTurnPlayer2;
  }
}

export function renderBoard(
  container,
  board,
  attacks,
  showShips,
  clickable,
  onAttack,
) {
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
          onAttack([r, c]);
        };
      }

      container.appendChild(cell);
    }
  }
}

export function renderPlacementBoard(player) {
  const container = boardContainerFor(player);
  container.innerHTML = "";
  const { placementBoard } = uiState.players[player];

  for (let r = 0; r < BOARD_SIZE; r++) {
    for (let c = 0; c < BOARD_SIZE; c++) {
      const cell = document.createElement("div");
      cell.className = "cell";
      cell.dataset.row = r;
      cell.dataset.col = c;
      cell.dataset.player = player;
      if (placementBoard?.[r][c]) {
        cell.classList.add("ship", `ship-${placementBoard[r][c]}`);
      }
      container.appendChild(cell);
    }
  }
}

function shipListIdFor(player) {
  if (player === "player2") return "ship-list-2";
  return uiState.mode === "aivai" ? "ship-list-1" : "ship-list";
}

export function renderPlacementShipList(player) {
  const list = document.getElementById(shipListIdFor(player));
  if (!list) return;
  list.innerHTML = "";

  const { pendingShips, placedShips } = uiState.players[player];

  for (const ship of pendingShips) {
    const li = document.createElement("li");
    li.textContent = SHIP_LABELS[ship];
    li.dataset.ship = ship;
    li.dataset.player = player;
    li.style.cursor = "grab";
    li.onpointerdown = (e) => {
      e.preventDefault();
      uiState.drag.ship = {
        name: ship,
        dir: uiState.players[player].currentDir,
        player,
      };
      li.classList.add("dragging");
    };
    list.appendChild(li);
  }

  for (const ship of placedShips) {
    const li = document.createElement("li");
    li.textContent = SHIP_LABELS[ship];
    li.className = "placed";
    list.appendChild(li);
  }
}

export function clearPlacementPreview(player) {
  boardContainerFor(player)
    .querySelectorAll(".cell")
    .forEach((el) => el.classList.remove("preview-valid", "preview-invalid"));
}

export function renderPlacementPreview(player, cells, valid) {
  clearPlacementPreview(player);
  if (!cells?.length) return;
  const previewSet = new Set(cells.map(([r, c]) => `${r * BOARD_SIZE + c}`));
  boardContainerFor(player)
    .querySelectorAll(".cell")
    .forEach((el, idx) => {
      if (previewSet.has(`${idx}`)) {
        el.classList.add(valid ? "preview-valid" : "preview-invalid");
      }
    });
}

import { uiState } from "./state.js";
import { clearPlacementPreview } from "./render.js";

function validatePreviewAt(r, c, worker) {
  const { ship } = uiState.drag;
  if (!ship) return;
  worker.postMessage({
    type: "validate_placement",
    ship: ship.name,
    row: r,
    col: c,
    dir: ship.dir,
    player: ship.player,
  });
}

function rotateBtnFor(player) {
  if (uiState.mode === "aivai" || player === "player2") {
    return document.querySelector(`.btn-rotate-side[data-player='${player}']`);
  }
  return document.getElementById("btn-rotate");
}

export function toggleDir(player, worker) {
  const ps = uiState.players[player];
  ps.currentDir = ps.currentDir === "h" ? "v" : "h";
  if (uiState.drag.ship?.player === player) {
    uiState.drag.ship.dir = ps.currentDir;
  }
  const btn = rotateBtnFor(player);
  if (btn) {
    btn.textContent = `↕ Rotacionar (R) — ${ps.currentDir === "h" ? "Horizontal" : "Vertical"}`;
  }
  if (uiState.drag.ship?.player === player && uiState.drag.cell) {
    validatePreviewAt(uiState.drag.cell.row, uiState.drag.cell.col, worker);
  }
}

export function initPlacementHandlers(worker) {
  document.getElementById("btn-rotate").onclick = () =>
    toggleDir("player1", worker);
  document.getElementById("btn-shuffle").onclick = () =>
    worker.postMessage({ type: "random_placement", player: "player1" });
  document.getElementById("btn-clear").onclick = () =>
    worker.postMessage({ type: "clear_placement", player: "player1" });

  document.querySelectorAll(".btn-rotate-side").forEach((btn) => {
    btn.onclick = () => toggleDir(btn.dataset.player, worker);
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
      worker.postMessage({
        type: "clear_placement",
        player: btn.dataset.player,
      });
  });

  document.addEventListener("pointermove", (e) => {
    const { ship, cell } = uiState.drag;
    if (!ship) return;

    const el = document.elementFromPoint(e.clientX, e.clientY);
    const cellEl = el?.closest?.("[data-row]");

    if (cellEl) {
      const cellPlayer = cellEl.dataset.player;
      if (cellPlayer && cellPlayer !== ship.player) return;

      const r = +cellEl.dataset.row;
      const c = +cellEl.dataset.col;

      if (!cell || cell.row !== r || cell.col !== c) {
        uiState.drag.cell = { row: r, col: c };
        validatePreviewAt(r, c, worker);
      }
    } else {
      if (cell) {
        uiState.drag.cell = null;
        clearPlacementPreview(ship.player);
      }
    }
  });

  document.addEventListener("pointerup", () => {
    const { ship, cell } = uiState.drag;
    if (!ship) return;

    if (cell) {
      worker.postMessage({
        type: "place_ship",
        ship: ship.name,
        row: cell.row,
        col: cell.col,
        dir: ship.dir,
        player: ship.player,
      });
    }

    document
      .querySelectorAll(".dragging")
      .forEach((el) => el.classList.remove("dragging"));
    const prevPlayer = ship.player;
    uiState.drag.ship = null;
    uiState.drag.cell = null;
    clearPlacementPreview(prevPlayer);
  });

  document.addEventListener("keydown", (e) => {
    if ((e.key === "r" || e.key === "R") && uiState.phase === "placement") {
      toggleDir(uiState.drag.ship?.player ?? "player1", worker);
    }
  });
}

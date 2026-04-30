import { uiState } from "./state.js"
import { clearPlacementPreview } from "./render.js"

function validatePreviewAt(r, c, engine) {
  const { ship } = uiState.drag
  if (!ship) return
  engine.canPlaceShip(ship.name, r, c, ship.dir, ship.player)
}

function rotateBtnFor(player) {
  if (uiState.mode === "aivai" || player === "player2") {
    return document.querySelector(`.btn-rotate-side[data-player='${player}']`)
  }
  return document.getElementById("btn-rotate")
}

export function toggleDir(player, engine) {
  const ps = uiState.players[player]
  ps.currentDir = ps.currentDir === "h" ? "v" : "h"
  if (uiState.drag.ship?.player === player) {
    uiState.drag.ship.dir = ps.currentDir
  }
  const btn = rotateBtnFor(player)
  if (btn) {
    btn.textContent = `↕ Rotacionar (R) — ${ps.currentDir === "h" ? "Horizontal" : "Vertical"}`
  }
  if (uiState.drag.ship?.player === player && uiState.drag.cell) {
    validatePreviewAt(uiState.drag.cell.row, uiState.drag.cell.col, engine)
  }
}

export function initPlacementHandlers(engine) {
  document.getElementById("btn-rotate").onclick = () => toggleDir("player1", engine)
  document.getElementById("btn-shuffle").onclick = () => engine.randomPlacement("player1")
  document.getElementById("btn-clear").onclick = () => engine.clearPlacement("player1")

  document.querySelectorAll(".btn-rotate-side").forEach((btn) => {
    btn.onclick = () => toggleDir(btn.dataset.player, engine)
  })
  document.querySelectorAll(".btn-shuffle-side").forEach((btn) => {
    btn.onclick = () => engine.randomPlacement(btn.dataset.player)
  })
  document.querySelectorAll(".btn-clear-side").forEach((btn) => {
    btn.onclick = () => engine.clearPlacement(btn.dataset.player)
  })

  document.addEventListener("pointermove", (e) => {
    const { ship, cell } = uiState.drag
    if (!ship) return

    const el = document.elementFromPoint(e.clientX, e.clientY)
    const cellEl = el?.closest?.("[data-row]")

    if (cellEl) {
      const cellPlayer = cellEl.dataset.player
      if (cellPlayer && cellPlayer !== ship.player) return

      const r = +cellEl.dataset.row
      const c = +cellEl.dataset.col

      if (!cell || cell.row !== r || cell.col !== c) {
        uiState.drag.cell = { row: r, col: c }
        validatePreviewAt(r, c, engine)
      }
    } else {
      if (cell) {
        uiState.drag.cell = null
        clearPlacementPreview(ship.player)
      }
    }
  })

  document.addEventListener("pointerup", () => {
    const { ship, cell } = uiState.drag
    if (!ship) return

    if (cell) {
      engine.placeShip(ship.name, cell.row, cell.col, ship.dir, ship.player)
    }

    document.querySelectorAll(".dragging").forEach((el) => el.classList.remove("dragging"))
    const prevPlayer = ship.player
    uiState.drag.ship = null
    uiState.drag.cell = null
    clearPlacementPreview(prevPlayer)
  })

  document.addEventListener("keydown", (e) => {
    if ((e.key === "r" || e.key === "R") && uiState.phase === "placement") {
      toggleDir(uiState.drag.ship?.player ?? "player1", engine)
    }
  })
}

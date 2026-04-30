import {
  CMD_INIT, CMD_CAN_PLACE, CMD_PLACE_SHIP, CMD_RANDOM_PLACEMENT,
  CMD_CLEAR_PLACEMENT, CMD_START_GAME, CMD_ATTACK, CMD_AI_TURN,
  EVT_READY, EVT_PLACEMENT_STATE, EVT_PLACEMENT_VALID, EVT_STATE, EVT_ERROR,
} from "./protocol.js"

export function createEngine(
  callbacks,
  worker = new Worker(new URL("./worker.js", import.meta.url), { type: "module" }),
) {
  const { onReady, onPlacementState, onPlacementValid, onGameState, onError } = callbacks

  worker.onmessage = (e) => {
    const msg = e.data
    if (msg.type === EVT_READY)
      onReady?.()
    else if (msg.type === EVT_PLACEMENT_STATE)
      onPlacementState?.(msg.player, { pending: msg.pending, placed: msg.placed, board: msg.board ?? null })
    else if (msg.type === EVT_PLACEMENT_VALID)
      onPlacementValid?.(msg.player, msg.cells, msg.valid)
    else if (msg.type === EVT_STATE)
      onGameState?.(msg.state, msg.mode)
    else if (msg.type === EVT_ERROR)
      onError?.(msg.message)
  }

  return {
    init(mode) { worker.postMessage({ type: CMD_INIT, mode }) },
    canPlaceShip(ship, row, col, dir, player) { worker.postMessage({ type: CMD_CAN_PLACE, ship, row, col, dir, player }) },
    placeShip(ship, row, col, dir, player) { worker.postMessage({ type: CMD_PLACE_SHIP, ship, row, col, dir, player }) },

    randomPlacement(player) { worker.postMessage({ type: CMD_RANDOM_PLACEMENT, player }) },
    clearPlacement(player) { worker.postMessage({ type: CMD_CLEAR_PLACEMENT, player }) },

    startGame(mode) { worker.postMessage({ type: CMD_START_GAME, mode }) },
    attack(coord) { worker.postMessage({ type: CMD_ATTACK, coord }) },
    aiTurn() { worker.postMessage({ type: CMD_AI_TURN }) },
  }
}

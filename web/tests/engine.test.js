import { createEngine } from "../src/engine.js"
import {
  CMD_INIT, CMD_CAN_PLACE, CMD_PLACE_SHIP, CMD_RANDOM_PLACEMENT,
  CMD_CLEAR_PLACEMENT, CMD_START_GAME, CMD_ATTACK, CMD_AI_TURN,
  EVT_READY, EVT_PLACEMENT_STATE, EVT_PLACEMENT_VALID, EVT_STATE, EVT_ERROR,
} from "../src/protocol.js"

function mockWorker() {
  return { postMessage: vi.fn(), onmessage: null }
}

test("init posts CMD_INIT with mode", () => {
  const worker = mockWorker()
  const engine = createEngine({}, worker)

  engine.init("hvai")

  expect(worker.postMessage).toHaveBeenCalledWith({ type: CMD_INIT, mode: "hvai" })
})

test("canPlaceShip posts CMD_CAN_PLACE with all fields", () => {
  const worker = mockWorker()
  const engine = createEngine({}, worker)

  engine.canPlaceShip("destroyer", 0, 0, "h", "player1")

  expect(worker.postMessage).toHaveBeenCalledWith({
    type: CMD_CAN_PLACE, ship: "destroyer", row: 0, col: 0, dir: "h", player: "player1",
  })
})

test("placeShip posts CMD_PLACE_SHIP with all fields", () => {
  const worker = mockWorker()
  const engine = createEngine({}, worker)

  engine.placeShip("carrier", 2, 3, "v", "player2")

  expect(worker.postMessage).toHaveBeenCalledWith({
    type: CMD_PLACE_SHIP, ship: "carrier", row: 2, col: 3, dir: "v", player: "player2",
  })
})

test("randomPlacement posts CMD_RANDOM_PLACEMENT with player", () => {
  const worker = mockWorker()
  const engine = createEngine({}, worker)

  engine.randomPlacement("player2")

  expect(worker.postMessage).toHaveBeenCalledWith({ type: CMD_RANDOM_PLACEMENT, player: "player2" })
})

test("clearPlacement posts CMD_CLEAR_PLACEMENT with player", () => {
  const worker = mockWorker()
  const engine = createEngine({}, worker)

  engine.clearPlacement("player1")

  expect(worker.postMessage).toHaveBeenCalledWith({ type: CMD_CLEAR_PLACEMENT, player: "player1" })
})

test("startGame posts CMD_START_GAME with mode", () => {
  const worker = mockWorker()
  const engine = createEngine({}, worker)

  engine.startGame("aivai")

  expect(worker.postMessage).toHaveBeenCalledWith({ type: CMD_START_GAME, mode: "aivai" })
})

test("attack posts CMD_ATTACK with coord", () => {
  const worker = mockWorker()
  const engine = createEngine({}, worker)

  engine.attack([3, 7])

  expect(worker.postMessage).toHaveBeenCalledWith({ type: CMD_ATTACK, coord: [3, 7] })
})

test("aiTurn posts CMD_AI_TURN", () => {
  const worker = mockWorker()
  const engine = createEngine({}, worker)

  engine.aiTurn()

  expect(worker.postMessage).toHaveBeenCalledWith({ type: CMD_AI_TURN })
})

test("EVT_READY triggers onReady callback", () => {
  const worker = mockWorker()
  const onReady = vi.fn()

  createEngine({ onReady }, worker)

  worker.onmessage({ data: { type: EVT_READY } })

  expect(onReady).toHaveBeenCalledOnce()
})

test("EVT_PLACEMENT_STATE triggers onPlacementState with player and state fields", () => {
  const worker = mockWorker()
  const onPlacementState = vi.fn()

  createEngine({ onPlacementState }, worker)

  worker.onmessage({
    data: {
      type: EVT_PLACEMENT_STATE, player: "player1",
      pending: ["carrier"], placed: ["destroyer"], board: null,
    }
  })

  expect(onPlacementState).toHaveBeenCalledWith("player1", {
    pending: ["carrier"], placed: ["destroyer"], board: null,
  })
})

test("EVT_PLACEMENT_VALID triggers onPlacementValid with player, cells, valid", () => {
  const worker = mockWorker()
  const onPlacementValid = vi.fn()

  createEngine({ onPlacementValid }, worker)

  worker.onmessage({
    data: {
      type: EVT_PLACEMENT_VALID, player: "player2", cells: [[0, 0], [0, 1]], valid: true,
    }
  })

  expect(onPlacementValid).toHaveBeenCalledWith("player2", [[0, 0], [0, 1]], true)
})

test("EVT_STATE triggers onGameState with state and mode", () => {
  const worker = mockWorker()
  const onGameState = vi.fn()

  createEngine({ onGameState }, worker)

  const state = { current_turn: "player1", winner: null }

  worker.onmessage({ data: { type: EVT_STATE, state, mode: "hvai" } })

  expect(onGameState).toHaveBeenCalledWith(state, "hvai")
})

test("EVT_ERROR triggers onError with message string", () => {
  const worker = mockWorker()
  const onError = vi.fn()

  createEngine({ onError }, worker)

  worker.onmessage({ data: { type: EVT_ERROR, message: "boom" } })

  expect(onError).toHaveBeenCalledWith("boom")
})

test("unknown event type does not throw", () => {
  const worker = mockWorker()

  createEngine({}, worker)

  expect(() => worker.onmessage({ data: { type: "unknown" } })).not.toThrow()
})

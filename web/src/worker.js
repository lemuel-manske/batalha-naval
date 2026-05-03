import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.mjs"
import {
  CMD_INIT, CMD_CAN_PLACE, CMD_PLACE_SHIP, CMD_RANDOM_PLACEMENT,
  CMD_CLEAR_PLACEMENT, CMD_START_GAME, CMD_ATTACK, CMD_AI_TURN,
  EVT_READY, EVT_PLACEMENT_STATE, EVT_PLACEMENT_VALID, EVT_STATE, EVT_ERROR,
} from "./protocol.js"

let pyodide = null

async function initPyodide() {
  pyodide = await loadPyodide()

  const modules = [
    "__init__", "board", "utils", "game", "loop",
    "strategies/__init__", "strategies/types", "strategies/random",
    "strategies/randomic_based_mcts", "strategies/classic_mcts",
    "strategies/heuristic_based_mcts",
  ]

  pyodide.FS.mkdirTree("/batalha_naval")
  pyodide.FS.mkdirTree("/batalha_naval/strategies")
  for (const mod of modules) {
    const url = new URL(`../batalha_naval/${mod}.py`, self.location.href).href
    const resp = await fetch(url)
    const src = await resp.text()
    pyodide.FS.writeFile(`/batalha_naval/${mod}.py`, src)
  }

  pyodide.runPython(`
import sys
sys.path.insert(0, "/")
`)

  pyodide.runPython(`
from batalha_naval.board import empty_board, random_placement, SHIPS, can_place_ship, place_ship, BOARD_SIZE
from batalha_naval.game import new_game, attack as _attack, is_game_over, get_winner
from batalha_naval.strategies import random_strategy, mcts_classic_strategy, mcts_random_strategy
import json as _json

_STRATEGIES = {
    "random": random_strategy,
    "smart":  mcts_classic_strategy,
    "mcts":   mcts_random_strategy,
}

_strategy1 = mcts_classic_strategy
_strategy2 = mcts_classic_strategy
`)

  pyodide.runPython(`
def _serialize_state(state):
    def coord_set(s):
        return [list(c) for c in s]
    return _json.dumps({
        "attacks": {p: coord_set(state["attacks"][p]) for p in ["player1", "player2"]},
        "ships": {
            p: {ship: coord_set(cells) for ship, cells in state["ships"][p].items()}
            for p in ["player1", "player2"]
        },
        "boards": {p: [list(row) for row in state["boards"][p]] for p in ["player1", "player2"]},
        "current_turn": state["current_turn"],
        "winner": state["winner"],
    })
`)

  self.postMessage({ type: EVT_READY })
}

function serializeState() {
  return pyodide.runPython(`_serialize_state(_state)`)
}

self.onmessage = async function(e) {
  const msg = e.data
  try {
    if (msg.type === CMD_INIT) await handleInit(msg.mode)
    else if (msg.type === CMD_CAN_PLACE) handleValidatePlacement(msg)
    else if (msg.type === CMD_PLACE_SHIP) handlePlaceShip(msg)
    else if (msg.type === CMD_RANDOM_PLACEMENT) handleRandomPlacement(msg.player)
    else if (msg.type === CMD_CLEAR_PLACEMENT) handleClearPlacement(msg.player)
    else if (msg.type === CMD_START_GAME) handleStartGame(msg.mode, msg.strategy)
    else if (msg.type === CMD_ATTACK) handleAttack(msg.coord)
    else if (msg.type === CMD_AI_TURN) handleAiTurn()
  } catch (err) {
    self.postMessage({ type: EVT_ERROR, message: err.message })
  }
}

function handleInit(mode) {
  if (mode === "aivai") {
    pyodide.runPython(`
_placement_board  = empty_board()
_placement_board2 = empty_board()
`)
    _sendPlacementState("player1")
    _sendPlacementState("player2")
  } else {
    pyodide.runPython(`_placement_board = empty_board()`)
    _sendPlacementState("player1")
  }
}

function handleValidatePlacement({ ship, row, col, dir, player }) {
  const boardVar = player === "player2" ? "_placement_board2" : "_placement_board"
  const result = pyodide.runPython(`
_valid = can_place_ship(${boardVar}, "${ship}", (${row}, ${col}), "${dir}")
_size = SHIPS["${ship}"]
if "${dir}" == "h":
    _cells = [[${row}, ${col} + i] for i in range(_size)]
else:
    _cells = [[${row} + i, ${col}] for i in range(_size)]
_json.dumps({"valid": _valid, "cells": _cells if _valid else []})
`)
  self.postMessage({
    type: EVT_PLACEMENT_VALID,
    player: player || "player1",
    ...JSON.parse(result),
  })
}

function handlePlaceShip({ ship, row, col, dir, player }) {
  const boardVar = player === "player2" ? "_placement_board2" : "_placement_board"
  const valid = pyodide.runPython(
    `can_place_ship(${boardVar}, "${ship}", (${row}, ${col}), "${dir}")`,
  )
  if (!valid) {
    console.warn(`[worker] posicionamento ignorado: ${ship} em (${row},${col}) dir=${dir} player=${player}`)
    _sendPlacementState(player || "player1")
    return
  }
  pyodide.runPython(
    `${boardVar} = place_ship(${boardVar}, "${ship}", (${row}, ${col}), "${dir}")`,
  )
  _sendPlacementState(player || "player1")
}

function handleRandomPlacement(player) {
  const boardVar = player === "player2" ? "_placement_board2" : "_placement_board"
  pyodide.runPython(`${boardVar} = random_placement()`)
  _sendPlacementState(player || "player1")
}

function handleClearPlacement(player) {
  const boardVar = player === "player2" ? "_placement_board2" : "_placement_board"
  pyodide.runPython(`${boardVar} = empty_board()`)
  _sendPlacementState(player || "player1")
}

function _sendPlacementState(player) {
  const boardVar = player === "player2" ? "_placement_board2" : "_placement_board"
  const result = pyodide.runPython(`
_placed_names = []
_pending_names = []
for _ship_name in SHIPS:
    _found = any(
        ${boardVar}[r][c] == _ship_name
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
    )
    (_placed_names if _found else _pending_names).append(_ship_name)
_board_rows = [list(row) for row in ${boardVar}]
_json.dumps({"placed": _placed_names, "pending": _pending_names, "board": _board_rows})
`)
  self.postMessage({
    type: EVT_PLACEMENT_STATE,
    player: player || "player1",
    ...JSON.parse(result),
  })
}

function handleStartGame(mode, strategy) {
  const s = strategy || {}

  if (mode === "aivai") {
    const s1 = s.p1_aivai || "smart"
    const s2 = s.p2_aivai || "smart"
    pyodide.runPython(`
_strategy1 = _STRATEGIES["${s1}"]
_strategy2 = _STRATEGIES["${s2}"]
_state = new_game(_placement_board, _placement_board2)
`)
    self.postMessage({ type: EVT_STATE, state: JSON.parse(serializeState()), mode: "aivai" })
  } else {
    const s1 = s.hvai || "smart"
    pyodide.runPython(`
_strategy1 = _STRATEGIES["${s1}"]
_strategy2 = _STRATEGIES["${s1}"]
_board2 = random_placement()
_state = new_game(_placement_board, _board2)
`)
    self.postMessage({ type: EVT_STATE, state: JSON.parse(serializeState()), mode: "hvai" })
  }
}

function handleAttack(coord) {
  pyodide.runPython(`
_state, _result = _attack(_state, "player1", (${coord[0]}, ${coord[1]}))
if is_game_over(_state):
    _state = {**_state, "winner": get_winner(_state)}
`)
  self.postMessage({ type: EVT_STATE, state: JSON.parse(serializeState()) })
}

function handleAiTurn() {
  const alreadyOver = pyodide.runPython(`is_game_over(_state)`)
  if (alreadyOver) return
  pyodide.runPython(`
_current = _state["current_turn"]
_strat = _strategy1 if _current == "player1" else _strategy2
_coord = _strat(_state, _current)
_state, _result = _attack(_state, _current, _coord)
if is_game_over(_state):
    _state = {**_state, "winner": get_winner(_state)}
`)
  self.postMessage({ type: EVT_STATE, state: JSON.parse(serializeState()) })
}

initPyodide().catch((err) =>
  self.postMessage({ type: EVT_ERROR, message: err.message }),
)

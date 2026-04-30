importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js");

let pyodide = null;

async function initPyodide() {
  pyodide = await loadPyodide();

  // monta os módulos Python no filesystem virtual do Pyodide
  const modules = ["__init__", "board", "utils", "game", "strategy", "loop"];

  pyodide.FS.mkdirTree("/batalha_naval");
  for (const mod of modules) {
    const url = new URL(`./batalha_naval/${mod}.py`, self.location.href).href;
    const resp = await fetch(url);
    const src = await resp.text();
    pyodide.FS.writeFile(`/batalha_naval/${mod}.py`, src);
  }

  // adiciona o diretório raiz ao sys.path para que `import batalha_naval` funcione
  pyodide.runPython(`
import sys
sys.path.insert(0, "/")
`);

  // importa tudo uma vez aqui para evitar re-imports em cada handler
  pyodide.runPython(`
from batalha_naval.board import empty_board, random_placement, SHIPS, can_place_ship, place_ship, BOARD_SIZE
from batalha_naval.game import new_game, attack as _attack, is_game_over, get_winner, is_valid_attack
from batalha_naval.strategy import smart_strategy, random_strategy
from batalha_naval.loop import run_game
import json as _json
`);

  // define _serialize_state uma vez (refinamento 1 — evitar redefinir a cada chamada)
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
`);

  self.postMessage({ type: "ready" });
}

// serializa _state global Python para JSON
function serializeState() {
  return pyodide.runPython(`_serialize_state(_state)`);
}

self.onmessage = async function (e) {
  const msg = e.data;
  try {
    if (msg.type === "init") {
      await handleInit(msg.mode);
    } else if (msg.type === "can_place_ship") {
      handleValidatePlacement(msg);
    } else if (msg.type === "place_ship") {
      handlePlaceShip(msg);
    } else if (msg.type === "random_placement") {
      handleRandomPlacement(msg.player);
    } else if (msg.type === "clear_placement") {
      handleClearPlacement(msg.player);
    } else if (msg.type === "start_game") {
      handleStartGame(msg.mode);
    } else if (msg.type === "attack") {
      handleAttack(msg.coord);
    } else if (msg.type === "ai_turn") {
      handleAiTurn();
    }
  } catch (err) {
    self.postMessage({ type: "error", message: err.message });
  }
};

function handleInit(mode) {
  if (mode === "aivai") {
    pyodide.runPython(`
_placement_board  = empty_board()
_placement_board2 = empty_board()
`);
    _sendPlacementState("player1");
    _sendPlacementState("player2");
  } else {
    pyodide.runPython(`_placement_board = empty_board()`);
    _sendPlacementState("player1");
  }
}

function handleValidatePlacement({ ship, row, col, dir, player }) {
  const boardVar =
    player === "player2" ? "_placement_board2" : "_placement_board";
  const result = pyodide.runPython(`
_valid = can_place_ship(${boardVar}, "${ship}", (${row}, ${col}), "${dir}")
_size = SHIPS["${ship}"]
if "${dir}" == "h":
    _cells = [[${row}, ${col} + i] for i in range(_size)]
else:
    _cells = [[${row} + i, ${col}] for i in range(_size)]
_json.dumps({"valid": _valid, "cells": _cells if _valid else []})
`);
  self.postMessage({
    type: "placement_valid",
    player: player || "player1",
    ...JSON.parse(result),
  });
}

function handlePlaceShip({ ship, row, col, dir, player }) {
  const boardVar =
    player === "player2" ? "_placement_board2" : "_placement_board";
  const valid = pyodide.runPython(
    `can_place_ship(${boardVar}, "${ship}", (${row}, ${col}), "${dir}")`,
  );
  if (!valid) {
    console.warn(
      `[worker] posicionamento ignorado: ${ship} em (${row},${col}) dir=${dir} player=${player}`,
    );
    _sendPlacementState(player || "player1");
    return;
  }
  pyodide.runPython(
    `${boardVar} = place_ship(${boardVar}, "${ship}", (${row}, ${col}), "${dir}")`,
  );
  _sendPlacementState(player || "player1");
}

function handleRandomPlacement(player) {
  const boardVar =
    player === "player2" ? "_placement_board2" : "_placement_board";
  pyodide.runPython(`${boardVar} = random_placement()`);
  _sendPlacementState(player || "player1");
}

function handleClearPlacement(player) {
  const boardVar =
    player === "player2" ? "_placement_board2" : "_placement_board";
  pyodide.runPython(`${boardVar} = empty_board()`);
  _sendPlacementState(player || "player1");
}

function _sendPlacementState(player) {
  const boardVar =
    player === "player2" ? "_placement_board2" : "_placement_board";
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
`);
  self.postMessage({
    type: "placement_state",
    player: player || "player1",
    ...JSON.parse(result),
  });
}

function handleStartGame(mode) {
  if (mode === "aivai") {
    pyodide.runPython(`_state = new_game(_placement_board, _placement_board2)`);
    self.postMessage({
      type: "state",
      state: JSON.parse(serializeState()),
      mode: "aivai",
    });
  } else {
    pyodide.runPython(`
_board2 = random_placement()
_state = new_game(_placement_board, _board2)
`);
    self.postMessage({
      type: "state",
      state: JSON.parse(serializeState()),
      mode: "hvai",
    });
  }
}

function handleAttack(coord) {
  pyodide.runPython(`
_state, _result = _attack(_state, "player1", (${coord[0]}, ${coord[1]}))
if is_game_over(_state):
    _state = {**_state, "winner": get_winner(_state)}
`);
  self.postMessage({ type: "state", state: JSON.parse(serializeState()) });
}

function handleAiTurn() {
  const alreadyOver = pyodide.runPython(`is_game_over(_state)`);
  if (alreadyOver) return;
  pyodide.runPython(`
_coord = smart_strategy(_state, _state["current_turn"])
_state, _result = _attack(_state, _state["current_turn"], _coord)
if is_game_over(_state):
    _state = {**_state, "winner": get_winner(_state)}
`);
  self.postMessage({ type: "state", state: JSON.parse(serializeState()) });
}

// inicializa ao carregar o Worker
initPyodide().catch((err) =>
  self.postMessage({ type: "error", message: err.message }),
);

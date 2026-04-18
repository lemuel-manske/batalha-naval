from batalha_naval.board import Board, Coord, ShipName, BOARD_SIZE
from typing import Literal

type Player = str  # "player1" | "player2"

type ShipCells = frozenset[Coord]
type ShipMap = dict[ShipName, ShipCells]

type GameState = dict


type AttackResult = Literal["miss", "hit", "sunk"]


def _extract_ships(board: Board) -> ShipMap:
    ships: dict[ShipName, set[Coord]] = {}

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            name = board[r][c]
            if name is not None:
                ships.setdefault(name, set()).add((r, c))

    return {name: frozenset(cells) for name, cells in ships.items()}


def new_game(board1: Board, board2: Board) -> GameState:
    return {
        "boards": {
            "player1": board1,
            "player2": board2,
        },
        "ships": {
            "player1": _extract_ships(board1),
            "player2": _extract_ships(board2),
        },
        "attacks": {
            "player1": frozenset(),
            "player2": frozenset(),
        },
        "current_turn": "player1",
        "winner": None,
    }


def attack(
    state: GameState,
    attacker: Player,
    coord: Coord,
) -> tuple[GameState, AttackResult]:
    opponent: Player = "player2" if attacker == "player1" else "player1"
    r, c = coord
    cell = state["boards"][opponent][r][c]

    new_attacks = {
        **state["attacks"],
        attacker: state["attacks"][attacker] | frozenset({coord}),
    }
    # o turno sempre passa para o oponente, independente do resultado
    next_turn: Player = opponent

    if cell is None:
        return {**state, "attacks": new_attacks, "current_turn": next_turn}, "miss"

    ship_name: ShipName = cell
    remaining: ShipCells = state["ships"][opponent][ship_name] - frozenset({coord})

    if remaining:
        new_ships = {
            **state["ships"],
            opponent: {**state["ships"][opponent], ship_name: remaining},
        }
        return (
            {**state, "attacks": new_attacks, "ships": new_ships, "current_turn": next_turn},
            "hit",
        )

    # navio sem células restantes — remove do mapa
    new_opponent_ships = {
        k: v for k, v in state["ships"][opponent].items() if k != ship_name
    }
    new_ships = {**state["ships"], opponent: new_opponent_ships}

    return (
        {**state, "attacks": new_attacks, "ships": new_ships, "current_turn": next_turn},
        "sunk",
    )


def is_game_over(state: GameState) -> bool:
    return (
        len(state["ships"]["player1"]) == 0
        or len(state["ships"]["player2"]) == 0
    )


def get_winner(state: GameState) -> Player | None:
    if len(state["ships"]["player2"]) == 0:
        return "player1"

    if len(state["ships"]["player1"]) == 0:
        return "player2"

    return None


def is_valid_attack(
    state: GameState,
    attacker: Player,
    coord: Coord,
) -> bool:
    r, c = coord

    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
        return False

    return coord not in state["attacks"][attacker]

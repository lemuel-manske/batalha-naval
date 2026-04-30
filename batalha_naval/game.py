from typing import Literal

from batalha_naval.board import (
    BOARD_SIZE,
    Board,
    Coord,
)
from batalha_naval.utils import extract_ships

type Player = Literal["player1", "player2"]

type GameState = dict


type AttackResult = Literal["miss", "hit", "sunk"]


def opponent(player: Player) -> Player:
    '''
    Returns the opponent player.
    '''

    return "player2" if player == "player1" else "player1"


def new_game(board1: Board, board2: Board) -> GameState:
    '''
    Inits the game.
    '''

    return {
        "boards": {
            "player1": board1,
            "player2": board2,
        },
        "ships": {
            "player1": extract_ships(board1),
            "player2": extract_ships(board2),
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
    '''
    Executes an attack from the attacker player to the opponent at the given coordinate.
    '''

    opp = opponent(attacker)

    r, c = coord
    cell = state["boards"][opp][r][c]

    new_attacks = {
        **state["attacks"],
        attacker: state["attacks"][attacker] | frozenset({coord}),
    }
    # o turno sempre passa para o oponente, independente do resultado
    next_turn = opp

    if cell is None:
        return {**state, "attacks": new_attacks, "current_turn": next_turn}, "miss"

    ship_name = cell
    remaining = state["ships"][opp][ship_name] - frozenset({coord})

    if remaining:
        new_ships = {
            **state["ships"],
            opp: {**state["ships"][opp], ship_name: remaining},
        }
        return (
            {
                **state,
                "attacks": new_attacks,
                "ships": new_ships,
                "current_turn": next_turn,
            },
            "hit",
        )

    # navio sem células restantes, então remove do mapa (sunk)
    new_opponent_ships = {
        k: v for k, v in state["ships"][opp].items() if k != ship_name
    }
    new_ships = {**state["ships"], opp: new_opponent_ships}

    return (
        {
            **state,
            "attacks": new_attacks,
            "ships": new_ships,
            "current_turn": next_turn,
        },
        "sunk",
    )


def is_game_over(state: GameState) -> bool:
    '''
    Checks if the game is over.
    '''

    return len(state["ships"]["player1"]) == 0 or len(state["ships"]["player2"]) == 0


def get_winner(state: GameState) -> Player | None:
    '''
    Returns the winner player if the game is over, otherwise returns `None`.
    '''

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
    '''
    Validates if the attack from the attacker player to the opponent at the given coordinate is valid (i.e., within bounds and not previously attacked).
    '''

    r, c = coord

    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
        return False

    return coord not in state["attacks"][attacker]

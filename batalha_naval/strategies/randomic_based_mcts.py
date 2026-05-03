import time

from batalha_naval.board import BOARD_SIZE, Coord
from batalha_naval.game import (
    GameState,
    Player,
    attack,
    get_winner,
    opponent,
    sample_opponent_board,
)
from batalha_naval.utils import extract_ships

from .random import random_strategy
from .types import Strategies


def mcts_random_strategy(
    state: GameState, player: Player, time_budget: float = 0.4
) -> Coord:
    """
    A Monte Carlo Tree Search strategy that simulates random completions.

    Samples possible opponent boards consistent with known information,
    simulates games from those samples using random play, and tallies
    which candidate moves lead to wins more often. Anytime: more time
    yields better estimates.
    """

    opp = opponent(player)
    attacked = state["attacks"][player]
    candidates = [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if (r, c) not in attacked
    ]

    simulated_wins: dict[Coord, int] = {coord: 0 for coord in candidates}

    p1: Player = "player1"
    p2: Player = "player2"

    strategies: Strategies = {
        p1: random_strategy,
        p2: random_strategy,
    }

    from batalha_naval.loop import run_game

    deadline = time.monotonic() + time_budget

    while time.monotonic() < deadline:
        sampled_board = sample_opponent_board(state, player)

        simulated_state = {
            **state,
            "boards": {**state["boards"], opp: sampled_board},
            "ships": {
                **state["ships"],
                opp: extract_ships(sampled_board),
            },
        }

        for coord in candidates:
            sim, _ = attack(simulated_state, player, coord)
            final = run_game(sim, strategies)

            if get_winner(final) == player:
                simulated_wins[coord] += 1

    return max(candidates, key=lambda coord: simulated_wins[coord])

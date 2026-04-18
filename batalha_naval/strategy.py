import random

from typing import Callable

from batalha_naval.board import Coord, BOARD_SIZE
from batalha_naval.game import GameState, Player

type Strategy = Callable[[GameState, Player], Coord]


def random_strategy(state: GameState, player: Player) -> Coord:
    attacked = state["attacks"][player]

    candidates = [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if (r, c) not in attacked
    ]

    return random.choice(candidates)

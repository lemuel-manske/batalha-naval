import random

from batalha_naval.board import BOARD_SIZE, Coord
from batalha_naval.game import GameState, Player


def random_strategy(state: GameState, player: Player) -> Coord:
    """
    The simplest possible strategy.

    It just picks a random coordinate that hasn't been attacked yet.
    """

    attacked = state["attacks"][player]

    candidates = [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if (r, c) not in attacked
    ]

    return random.choice(candidates)

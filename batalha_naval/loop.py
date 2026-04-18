from batalha_naval.game import (
    AttackResult,
    GameState,
    Player,
    attack,
    is_game_over,
)
from batalha_naval.strategy import Strategy

type Strategies = dict[Player, Strategy]


def play_turn(
    state: GameState,
    strategies: Strategies,
) -> tuple[GameState, AttackResult]:
    current: Player = state["current_turn"]
    strategy: Strategy = strategies[current]

    coord = strategy(state, current)

    return attack(state, current, coord)


def run_game(
    state: GameState,
    strategies: Strategies,
) -> GameState:
    while not is_game_over(state):
        state, _ = play_turn(state, strategies)

    return state

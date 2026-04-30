from batalha_naval.game import (
    AttackResult,
    GameState,
    Player,
    attack,
    is_game_over,
)
from batalha_naval.strategy import Strategy

type Strategies = dict[Player, Strategy]


def run_game(
    state: GameState,
    strategies: Strategies,
) -> GameState:
    '''
    Runs the game until completion, using the provided strategies.
    '''

    while not is_game_over(state):
        state, _ = play_turn(state, strategies)

    return state


def play_turn(
    state: GameState,
    strategies: Strategies,
) -> tuple[GameState, AttackResult]:
    '''
    Executes a single turn in the game.
    '''

    current: Player = state["current_turn"]
    strategy: Strategy = strategies[current]

    coord = strategy(state, current)

    return attack(state, current, coord)

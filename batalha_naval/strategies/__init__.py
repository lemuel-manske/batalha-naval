from batalha_naval.strategies.heuristic_based_mcts import mcts_classic_strategy
from batalha_naval.strategies.random import random_strategy
from batalha_naval.strategies.randomic_based_mcts import mcts_random_strategy
from batalha_naval.strategies.types import Strategy, Strategies

__all__ = [
    "Strategy",
    "Strategies",
    "random_strategy",
    "mcts_random_strategy",
    "mcts_classic_strategy",
]

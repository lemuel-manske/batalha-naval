from typing import Callable

from batalha_naval.board import Coord
from batalha_naval.game import GameState, Player

type Strategy = Callable[[GameState, Player], Coord]
type Strategies = dict[Player, Strategy]

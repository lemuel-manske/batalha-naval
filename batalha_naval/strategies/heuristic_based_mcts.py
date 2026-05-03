import math
import random
import time

from dataclasses import dataclass, field
from itertools import groupby

from batalha_naval.board import BOARD_SIZE, Coord, SHIPS
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


def mcts_classic_strategy(
    state: GameState, player: Player, time_budget: float = 0.4
) -> Coord:
    """
    Classic MCTS adapted for Battleship's partial observability via determinization, with a heuristic default policy.
    """

    opp = opponent(player)

    attacked = state["attacks"][player]
    hot = _get_hot_cells(state, player)

    candidates = (
        _target_candidates(hot, attacked) if hot else _parity_candidates(state, player)
    )

    if len(candidates) == 1:
        return candidates[0]

    root = _Node(
        action=None,
        parent=None,
        untried_actions=list(candidates),
    )

    deadline = time.monotonic() + time_budget

    while time.monotonic() < deadline:
        sampled_board = sample_opponent_board(state, player)
        det_state = {
            **state,
            "boards": {**state["boards"], opp: sampled_board},
            "ships": {**state["ships"], opp: extract_ships(sampled_board)},
        }

        node = _select(root)

        if node.untried_actions:
            node = _expand(node)
        elif not node.children:
            pass

        reward = _simulate(det_state, node, player)

        _backpropagate(node, reward)

    if not root.children:
        return random.choice(candidates)

    # most visited node is the best move, as it was explored the most during the simulations
    # rather than just the one with the highest average reward, which could be skewed by outliers.
    coord = max(root.children, key=lambda n: n.n_visits).action
    assert coord is not None

    return coord


@dataclass
class _Node:
    action: Coord | None
    parent: "_Node | None"
    children: list["_Node"] = field(default_factory=list)
    n_visits: int = 0
    total_reward: float = 0.0
    untried_actions: list[Coord] = field(default_factory=list)


def _ucb(node: _Node, c: float = 1.41) -> float:
    '''
    The Upper Confidence Bound allows MCTS to balance:
    - Exploitation: favoring nodes with higher average reward (first term).
    - Exploration: favoring less-visited nodes to discover their potential (second term).
    '''

    if node.n_visits == 0:
        return float("inf")

    parent_visits = node.parent.n_visits if node.parent else 1

    return node.total_reward / node.n_visits + c * math.sqrt(
        math.log(parent_visits) / node.n_visits
    )


def _select(node: _Node) -> _Node:
    '''
    Selects the most promising node to explore, based on the UCB score, until it finds a leaf.
    '''

    while not node.untried_actions and node.children:
        node = max(node.children, key=_ucb)

    return node


def _expand(node: _Node) -> _Node:
    '''
    Expands the node by creating a new child for one of its untried actions (randomly selected).
    '''

    actions_size = len(node.untried_actions)
    random_action = random.randrange(actions_size)

    action = node.untried_actions.pop(random_action)

    child = _Node(action=action, parent=node)
    node.children.append(child)

    return child


def _simulate(det_state: GameState, node: _Node, player: Player) -> float:
    '''
    Simulates a game, and return a reward based on the outcome: winner > loser.
    '''

    from batalha_naval.loop import run_game

    def _heuristic_strategy(state: GameState, player: Player) -> Coord:
        attacked = state["attacks"][player]
        hot = _get_hot_cells(state, player)

        candidates = (
            _target_candidates(hot, attacked)
            if hot
            else _parity_candidates(state, player)
        )

        if not candidates:
            return random.choice(
                [
                    (r, c)
                    for r in range(BOARD_SIZE)
                    for c in range(BOARD_SIZE)
                    if (r, c) not in attacked
                ]
            )

        return random.choice(candidates)

    opp = opponent(player)

    coord = node.action
    assert coord is not None

    state_after_action, _ = attack(det_state, player, coord)

    # opponent plays randomly during rollouts, as the heuristic is focused on the main player chances of winning,
    # not on simulating a strong opponent # opponent plays randomly during rollouts,
    # as the heuristic is focused on the main player chances of winning, not on simulating a strong opponent
    strategies: Strategies = {
        player: _heuristic_strategy,
        opp: random_strategy, 
    }

    final = run_game(state_after_action, strategies)

    winner_reward = 1.0
    loser_reward = 0.0

    is_player_winner = get_winner(final) == player

    return winner_reward if is_player_winner else loser_reward


def _backpropagate(node: _Node | None, reward: float) -> None:
    '''
    Updates the node and its ancestors with the simulation result.
    '''

    while node is not None:
        node.n_visits += 1
        node.total_reward += reward
        node = node.parent


def _get_hot_cells(state: GameState, player: Player) -> list[Coord]:
    '''
    Cells that have been attacked and are hits on living ships, hence "hot" for targeting.
    '''

    opp = opponent(player)

    attacks = state["attacks"][player]
    opp_board = state["boards"][opp]

    living_ships = set(state["ships"][opp].keys())

    return [coord for coord in attacks if opp_board[coord[0]][coord[1]] in living_ships]


def _contiguous_runs(coords: list[Coord], axis: int) -> list[list[Coord]]:
    '''
    Given a list of coordinates and an axis (0 for rows, 1 for columns),
    returns a list of contiguous runs of coordinates along that axis.
    '''

    sorted_cells = sorted(coords, key=lambda x: x[axis])

    runs: list[list[Coord]] = []
    current: list[Coord] = [sorted_cells[0]]

    for cell in sorted_cells[1:]:
        if cell[axis] - current[-1][axis] == 1:
            current.append(cell)
        else:
            runs.append(current)
            current = [cell]

    runs.append(current)

    return runs


def _target_candidates(
    hot_cells: list[Coord],
    attacked: frozenset[Coord],
) -> list[Coord]:
    '''
    Candidate cells to attack when there are known hits on living ships.
    '''

    if not hot_cells:
        return []

    if len(hot_cells) == 1:
        r, c = hot_cells[0]
        neighbors = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [
            (nr, nc)
            for nr, nc in neighbors
            if 0 <= nr < BOARD_SIZE
            and 0 <= nc < BOARD_SIZE
            and (nr, nc) not in attacked
        ]

    rows = set(r for r, _ in hot_cells)
    cols = set(c for _, c in hot_cells)

    if len(rows) == 1:
        aligned = sorted(hot_cells, key=lambda x: x[1])
        r = aligned[0][0]
        min_c = aligned[0][1]
        max_c = aligned[-1][1]
        endpoints = [(r, min_c - 1), (r, max_c + 1)]
    elif len(cols) == 1:
        aligned = sorted(hot_cells, key=lambda x: x[0])
        c = aligned[0][1]
        min_r = aligned[0][0]
        max_r = aligned[-1][0]
        endpoints = [(min_r - 1, c), (max_r + 1, c)]
    else:
        clusters: list[list[Coord]] = []
        for _, group in groupby(sorted(hot_cells), key=lambda x: x[0]):
            cluster = list(group)
            if len(cluster) > 1:
                clusters.append(cluster)
        for _, group in groupby(
            sorted(hot_cells, key=lambda x: x[1]), key=lambda x: x[1]
        ):
            cluster = list(group)
            if len(cluster) > 1:
                clusters.append(cluster)
        if clusters:
            best_run: list[Coord] = []
            for cluster in clusters:
                axis = 1 if len(set(cell[0] for cell in cluster)) == 1 else 0
                for run in _contiguous_runs(cluster, axis):
                    if len(run) > len(best_run):
                        best_run = run
            return _target_candidates(best_run, attacked)
        best_cell = hot_cells[0]
        r, c = best_cell
        neighbors = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [
            (nr, nc)
            for nr, nc in neighbors
            if 0 <= nr < BOARD_SIZE
            and 0 <= nc < BOARD_SIZE
            and (nr, nc) not in attacked
        ]

    return [
        (er, ec)
        for er, ec in endpoints
        if 0 <= er < BOARD_SIZE and 0 <= ec < BOARD_SIZE and (er, ec) not in attacked
    ]


def _parity_candidates(state: GameState, player: Player) -> list[Coord]:
    '''
    Candidate cells to attack based on parity, considering the size of the smallest living ship.

    Ignores known hits, as it's meant to be a fallback when there are no "hot" cells.

    For example: in the first turn, the candidates will be *all* cells (as no attacks have been made).
    '''

    opp = opponent(player)

    attacked = state["attacks"][player]
    opp_board = state["boards"][opp]

    living_ships_sizes = [SHIPS[name] for name in state["ships"][opp]]
    min_ship_size = min(living_ships_sizes) if living_ships_sizes else 1

    known_misses: frozenset[Coord] = frozenset(
        coord for coord in attacked if opp_board[coord[0]][coord[1]] is None
    )

    candidates = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if (r, c) in attacked:
                continue

            fits_h = c + min_ship_size <= BOARD_SIZE and all(
                (r, c + i) not in known_misses for i in range(min_ship_size)
            )

            fits_v = r + min_ship_size <= BOARD_SIZE and all(
                (r + i, c) not in known_misses for i in range(min_ship_size)
            )

            if fits_h or fits_v:
                candidates.append((r, c))

    return candidates

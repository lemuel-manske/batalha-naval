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

    all_candidates: list[Coord] = []
    if hot:
        all_candidates = _target_candidates(hot, attacked)
    if not all_candidates:
        all_candidates = _parity_candidates(state, player)
    if not all_candidates:
        all_candidates = [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if (r, c) not in attacked
        ]

    if len(all_candidates) == 1:
        return all_candidates[0]

    root = _Node(
        action=None,
        parent=None,
        untried_actions=list(all_candidates),
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
        return random.choice(all_candidates)

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


def _heuristic_rollout_policy(state: GameState, player: Player) -> Coord:
    """
    Default policy for rollouts.

    Priority:
    1. Hunt: attack cells adjacent to known hits on living ships.
    2. Parity: attack cells where the smallest living ship could still fit.
    3. Fallback: random unattacked cell.
    """

    attacked = state["attacks"][player]
    hot = _get_hot_cells(state, player)

    if hot:
        candidates = _target_candidates(hot, attacked)

        if candidates:
            return random.choice(candidates)

    candidates = _parity_candidates(state, player)

    if candidates:
        return random.choice(candidates)

    return random_strategy(state, player)


def _ucb(node: _Node, c: float = 1.41) -> float:
    if node.n_visits == 0:
        return float("inf")

    parent_visits = node.parent.n_visits if node.parent else 1

    return node.total_reward / node.n_visits + c * math.sqrt(
        math.log(parent_visits) / node.n_visits
    )


def _select(node: _Node) -> _Node:
    while not node.untried_actions and node.children:
        node = max(node.children, key=_ucb)

    return node


def _expand(node: _Node) -> _Node:
    action = node.untried_actions.pop(random.randrange(len(node.untried_actions)))
    child = _Node(action=action, parent=node)
    node.children.append(child)
    return child


def _simulate(det_state: GameState, node: _Node, player: Player) -> float:
    from batalha_naval.loop import run_game

    opp = opponent(player)

    coord = node.action
    assert coord is not None

    state_after_action, _ = attack(det_state, player, coord)

    strategies: Strategies = {
        player: _heuristic_rollout_policy,
        opp: random_strategy,
    }

    final = run_game(state_after_action, strategies)

    return 1.0 if get_winner(final) == player else 0.0


def _backpropagate(node: _Node | None, reward: float) -> None:
    while node is not None:
        node.n_visits += 1
        node.total_reward += reward
        node = node.parent


def _get_hot_cells(state: GameState, player: Player) -> list[Coord]:
    opp = opponent(player)

    attacks = state["attacks"][player]
    opp_board = state["boards"][opp]

    living_ships = set(state["ships"][opp].keys())

    return [coord for coord in attacks if opp_board[coord[0]][coord[1]] in living_ships]


def _contiguous_runs(cells: list[Coord], axis: int) -> list[list[Coord]]:
    sorted_cells = sorted(cells, key=lambda x: x[axis])

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
    """Candidate cells to attack when there are known hits on living ships."""

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
    """Cells where the smallest living ship could still fit."""

    opp = opponent(player)

    attacked = state["attacks"][player]
    opp_board = state["boards"][opp]

    living_sizes = [SHIPS[name] for name in state["ships"][opp]]
    min_size = min(living_sizes) if living_sizes else 1

    known_misses: frozenset[Coord] = frozenset(
        coord for coord in attacked if opp_board[coord[0]][coord[1]] is None
    )

    candidates = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if (r, c) in attacked:
                continue

            fits_h = c + min_size <= BOARD_SIZE and all(
                (r, c + i) not in known_misses for i in range(min_size)
            )

            fits_v = r + min_size <= BOARD_SIZE and all(
                (r + i, c) not in known_misses for i in range(min_size)
            )

            if fits_h or fits_v:
                candidates.append((r, c))

    return candidates

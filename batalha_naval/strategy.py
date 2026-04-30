import random
import time

from itertools import groupby
from typing import Callable, Literal

from batalha_naval.board import (
    BOARD_SIZE,
    Board,
    Coord,
    SHIPS,
    can_place_ship,
    empty_board,
    place_ship,
)
from batalha_naval.game import (
    GameState,
    Player,
    attack,
    get_winner,
    opponent,
)
from batalha_naval.utils import extract_ships

'''
A strategy defines a function that, given the current game state and the player to move, returns a coordinate to attack.
'''
type Strategy = Callable[[GameState, Player], Coord]


def sample_opponent_board(state: GameState, attacker: Player) -> Board:
    opp = opponent(attacker)
    attacks = state["attacks"][attacker]
    opponent_board = state["boards"][opp]

    # células confirmadas como miss devem permanecer vazias na amostragem
    known_misses: frozenset[Coord] = frozenset(
        coord for coord in attacks if opponent_board[coord[0]][coord[1]] is None
    )

    # navios já afundados têm posição exata conhecida
    sunk_ships = set(SHIPS.keys()) - set(state["ships"][opp].keys())

    # reconstrói o tabuleiro com os navios afundados nas posições reais
    board = empty_board()
    rows = [list(row) for row in board]

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if opponent_board[r][c] in sunk_ships:
                rows[r][c] = opponent_board[r][c]

    board = tuple(tuple(row) for row in rows)

    # células confirmadas como hit de navios ainda vivos
    known_hits: frozenset[Coord] = frozenset(
        coord
        for coord in attacks
        if opponent_board[coord[0]][coord[1]] is not None
        and opponent_board[coord[0]][coord[1]] not in sunk_ships
    )

    # posiciona aleatoriamente os navios ainda vivos
    # respeitando misses e hits conhecidos
    for ship_name in state["ships"][opp]:
        placed = False

        while not placed:
            direction: Literal["h", "v"] = random.choice(["h", "v"])
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)

            if not can_place_ship(board, ship_name, (row, col), direction):
                continue

            size = SHIPS[ship_name]

            if direction == "h":
                cells = [(row, col + i) for i in range(size)]
            else:
                cells = [(row + i, col) for i in range(size)]

            if any(cell in known_misses for cell in cells):
                continue

            # hits conhecidos deste navio devem estar cobertos
            # pela posição sorteada
            ship_hits = {
                coord
                for coord in known_hits
                if opponent_board[coord[0]][coord[1]] == ship_name
            }
            if ship_hits and not ship_hits.issubset(set(cells)):
                continue

            board = place_ship(board, ship_name, (row, col), direction)
            placed = True

    return board


def random_strategy(state: GameState, player: Player) -> Coord:
    '''
    The simplest possible strategy.

    It just picks a random coordinate that hasn't been attacked yet.
    '''

    attacked = state["attacks"][player]

    candidates = [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if (r, c) not in attacked
    ]

    return random.choice(candidates)


def mcts_strategy(
    state: GameState, player: Player, time_budget: float = 0.4
) -> Coord:
    '''
    A more sophisticated strategy that uses Monte Carlo Tree Search (MCTS) to estimate the best move.

    The idea is to simulate many random completions of the game from the current state, using a simple strategy (like random) for both players.

    It differs from the pure random strategy in that it samples possible opponent boards consistent with known information, simulates games from those samples, and tallies which candidate moves lead to wins more often.

    It is constrained by a time budget, making it an anytime algorithm: the more time it has, the better its estimates become.
    '''

    from batalha_naval.game import opponent as get_opponent

    opp = get_opponent(player)

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
    strategies: dict[Player, Strategy] = {
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


def smart_strategy(state: GameState, player: Player) -> Coord:
    '''
    The most sophisticated strategy among the three provided.

    It combines two heuristics:
    - hunting (looking for cells adjacent to hits) and
    - targeting (looking for cells more likely to contain a ship, even without nearby hits).

    The flow is roughly: look for targets and then for adjacent hits.

    Techniques used:
    - For targeting, it samples possible opponent boards consistent
      with known hits and misses, and tallies how often each candidate
      cell contains a ship across the samples. This is a form of Monte Carlo estimation.

    - For hunting, it identifies "hot cells" (cells that are hits on still alive ships)
      and looks for contiguous runs of hits to determine likely orientations of the ship,
      then targets the endpoints of those runs.
      If there are no clear runs, it targets neighbors of the hot cells.
    '''

    attacked = state["attacks"][player]

    hot_cells = _get_hot_cells(state, player)

    if hot_cells:
        candidates = _target_candidates(hot_cells, attacked)
        if candidates:
            return random.choice(candidates)

    candidates = _parity_candidates(state, player)

    if not candidates:
        candidates = [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if (r, c) not in attacked
        ]

    if len(candidates) == 1:
        return candidates[0]

    tally: dict[Coord, int] = {coord: 0 for coord in candidates}

    N_SAMPLES = 200

    for _ in range(N_SAMPLES):
        sampled_board = sample_opponent_board(state, player)
        for coord in candidates:
            r, c = coord
            if sampled_board[r][c] is not None:
                tally[coord] += 1

    best_score = max(tally.values())
    best = [coord for coord, score in tally.items() if score == best_score]

    _CENTER = 4.5

    return min(
        best, key=lambda coord: abs(coord[0] - _CENTER) + abs(coord[1] - _CENTER)
    )


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


def _get_hot_cells(state: GameState, player: Player) -> list[Coord]:
    opp = opponent(player)
    attacks = state["attacks"][player]
    opp_board = state["boards"][opp]
    living_ships = set(state["ships"][opp].keys())
    return [coord for coord in attacks if opp_board[coord[0]][coord[1]] in living_ships]


def _target_candidates(
    hot_cells: list[Coord],
    attacked: frozenset[Coord],
) -> list[Coord]:
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

    rows = [r for r, _ in hot_cells]
    cols = [c for _, c in hot_cells]
    row_set = set(rows)
    col_set = set(cols)

    if len(row_set) == 1:
        aligned = sorted(hot_cells, key=lambda x: x[1])
        r = aligned[0][0]
        min_c = aligned[0][1]
        max_c = aligned[-1][1]
        endpoints = [(r, min_c - 1), (r, max_c + 1)]
    elif len(col_set) == 1:
        aligned = sorted(hot_cells, key=lambda x: x[0])
        c = aligned[0][1]
        min_r = aligned[0][0]
        max_r = aligned[-1][0]
        endpoints = [(min_r - 1, c), (max_r + 1, c)]
    else:
        clusters: list[list[Coord]] = []
        for r, group in groupby(sorted(hot_cells), key=lambda x: x[0]):
            cluster = list(group)
            if len(cluster) > 1:
                clusters.append(cluster)
        for c, group in groupby(
            sorted(hot_cells, key=lambda x: x[1]), key=lambda x: x[1]
        ):
            cluster = list(group)
            if len(cluster) > 1:
                clusters.append(cluster)
        if clusters:
            best_run: list[Coord] = []
            for cluster in clusters:
                axis = 1 if len(set(c[0] for c in cluster)) == 1 else 0
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

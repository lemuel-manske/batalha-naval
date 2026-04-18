import random
import time

from typing import Callable, Literal

from batalha_naval.board import (
    BOARD_SIZE,
    Board,
    Coord,
    SHIPS,
    empty_board,
    place_ship,
    validate_placement,
)
from batalha_naval.game import (
    GameState,
    Player,
    attack,
    get_winner,
)

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


def sample_opponent_board(state: GameState, attacker: Player) -> Board:
    opponent: Player = "player2" if attacker == "player1" else "player1"
    attacks = state["attacks"][attacker]
    opponent_board = state["boards"][opponent]

    # células confirmadas como miss devem permanecer vazias na amostragem
    known_misses: frozenset[Coord] = frozenset(
        coord for coord in attacks if opponent_board[coord[0]][coord[1]] is None
    )

    # navios já afundados têm posição exata conhecida
    sunk_ships = set(SHIPS.keys()) - set(state["ships"][opponent].keys())

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
    for ship_name in state["ships"][opponent]:
        placed = False

        while not placed:
            direction: Literal["h", "v"] = random.choice(["h", "v"])
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)

            if not validate_placement(board, ship_name, (row, col), direction):
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


MCTS_TIME_BUDGET = 0.4


def _extract_ships_from_board(board: Board) -> dict[str, frozenset[Coord]]:
    ships: dict[str, set[Coord]] = {}

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            name = board[r][c]
            if name is not None:
                ships.setdefault(name, set()).add((r, c))

    return {name: frozenset(cells) for name, cells in ships.items()}


def mcts_strategy(
    state: GameState, player: Player, time_budget: float = MCTS_TIME_BUDGET
) -> Coord:
    from batalha_naval.game import opponent as get_opponent

    opp: Player = get_opponent(player)

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

    # MCTS é um anytime algorithm: quanto mais tempo, melhor a estimativa.
    # o loop roda simulações até o budget expirar e retorna o melhor resultado
    # parcial — equivalente ao iterative deepening de Russell & Norvig cap. 5.
    deadline = time.monotonic() + time_budget
    while time.monotonic() < deadline:
        sampled_board = sample_opponent_board(state, player)

        simulated_state = {
            **state,
            "boards": {**state["boards"], opp: sampled_board},
            "ships": {
                **state["ships"],
                opp: _extract_ships_from_board(sampled_board),
            },
        }

        for coord in candidates:
            sim, _ = attack(simulated_state, player, coord)
            final = run_game(sim, strategies)

            if get_winner(final) == player:
                simulated_wins[coord] += 1

    return max(candidates, key=lambda coord: simulated_wins[coord])

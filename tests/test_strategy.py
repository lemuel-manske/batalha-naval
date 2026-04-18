from batalha_naval.board import random_placement, BOARD_SIZE
from batalha_naval.game import new_game
from batalha_naval.strategy import random_strategy


def test_random_strategy_returns_valid_coord():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    coord = random_strategy(state, "player1")
    r, c = coord
    assert 0 <= r < BOARD_SIZE
    assert 0 <= c < BOARD_SIZE


def test_random_strategy_does_not_repeat_attacked_coord():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    # atacar todas as coordenadas menos uma
    from batalha_naval.game import attack

    attacked: set = set()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if len(attacked) < BOARD_SIZE * BOARD_SIZE - 1:
                state, _ = attack(state, "player1", (r, c))
                attacked.add((r, c))
                # passa turno do player2
                remaining = [
                    (row, col)
                    for row in range(BOARD_SIZE)
                    for col in range(BOARD_SIZE)
                    if (row, col) not in state["attacks"]["player2"]
                ]
                if remaining:
                    state, _ = attack(state, "player2", remaining[0])
    coord = random_strategy(state, "player1")
    assert coord not in state["attacks"]["player1"]


from batalha_naval.board import SHIPS
from batalha_naval.game import attack as game_attack
from batalha_naval.strategy import sample_opponent_board


def test_sample_opponent_board_places_all_ships():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    sampled = sample_opponent_board(state, "player1")
    placed = {
        sampled[r][c]
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if sampled[r][c] is not None
    }
    assert placed == set(SHIPS.keys())


def test_sample_opponent_board_respects_known_hits():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    hit_coord = next(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if state["boards"]["player2"][r][c] is not None
    )
    state, _ = game_attack(state, "player1", hit_coord)
    miss_coord = next(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if state["boards"]["player1"][r][c] is None
        and (r, c) not in state["attacks"]["player2"]
    )
    state, _ = game_attack(state, "player2", miss_coord)
    sampled = sample_opponent_board(state, "player1")
    assert sampled[hit_coord[0]][hit_coord[1]] is not None


def test_sample_opponent_board_respects_known_misses():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    miss_coord = next(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if state["boards"]["player2"][r][c] is None
    )
    state, _ = game_attack(state, "player1", miss_coord)
    miss_coord2 = next(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if state["boards"]["player1"][r][c] is None
        and (r, c) not in state["attacks"]["player2"]
    )
    state, _ = game_attack(state, "player2", miss_coord2)
    sampled = sample_opponent_board(state, "player1")
    assert sampled[miss_coord[0]][miss_coord[1]] is None


from batalha_naval.strategy import mcts_strategy


def test_mcts_strategy_returns_valid_coord():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    coord = mcts_strategy(state, "player1", time_budget=0.05)
    r, c = coord
    assert 0 <= r < BOARD_SIZE
    assert 0 <= c < BOARD_SIZE


def test_mcts_strategy_does_not_return_attacked_coord():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    state, _ = game_attack(state, "player1", (0, 0))
    miss_coord2 = next(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if (r, c) not in state["attacks"]["player2"]
    )
    state, _ = game_attack(state, "player2", miss_coord2)
    coord = mcts_strategy(state, "player1", time_budget=0.05)
    assert coord not in state["attacks"]["player1"]

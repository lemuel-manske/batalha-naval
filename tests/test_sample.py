from batalha_naval.board import random_placement, BOARD_SIZE, SHIPS
from batalha_naval.game import new_game, attack
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
    state, _ = attack(state, "player1", hit_coord)
    miss_coord = next(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if state["boards"]["player1"][r][c] is None
        and (r, c) not in state["attacks"]["player2"]
    )
    state, _ = attack(state, "player2", miss_coord)
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
    state, _ = attack(state, "player1", miss_coord)
    miss_coord2 = next(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if state["boards"]["player1"][r][c] is None
        and (r, c) not in state["attacks"]["player2"]
    )
    state, _ = attack(state, "player2", miss_coord2)
    sampled = sample_opponent_board(state, "player1")
    assert sampled[miss_coord[0]][miss_coord[1]] is None

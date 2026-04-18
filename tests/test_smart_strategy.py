from batalha_naval.board import random_placement, BOARD_SIZE
from batalha_naval.game import new_game, attack
from batalha_naval.strategy import smart_strategy


def test_smart_strategy_returns_valid_coord():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    coord = smart_strategy(state, "player1")
    r, c = coord
    assert 0 <= r < BOARD_SIZE
    assert 0 <= c < BOARD_SIZE


def test_smart_strategy_does_not_return_attacked_coord():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    state, _ = attack(state, "player1", (0, 0))
    state, _ = attack(state, "player2", (9, 9))
    coord = smart_strategy(state, "player1")
    assert coord not in state["attacks"]["player1"]


def test_smart_strategy_targets_adjacent_after_hit():
    from batalha_naval.board import place_ship, empty_board

    board2 = empty_board()
    board2 = place_ship(board2, "destroyer", (5, 5), "h")
    board2 = place_ship(board2, "carrier", (0, 0), "h")
    board2 = place_ship(board2, "battleship", (2, 0), "h")
    board2 = place_ship(board2, "cruiser", (4, 0), "h")
    board2 = place_ship(board2, "submarine", (7, 0), "h")
    board1 = random_placement()
    state = new_game(board1, board2)
    state, result = attack(state, "player1", (5, 5))
    assert result == "hit"
    state, _ = attack(state, "player2", (9, 9))
    coord = smart_strategy(state, "player1")
    neighbors_of_hit = {(4, 5), (6, 5), (5, 4), (5, 6)}
    assert coord in neighbors_of_hit, f"Expected neighbor of hit, got {coord}"


def test_smart_strategy_continues_axis_after_two_hits():
    from batalha_naval.board import place_ship, empty_board

    board2 = empty_board()
    board2 = place_ship(board2, "carrier", (5, 3), "h")
    board2 = place_ship(board2, "battleship", (0, 0), "h")
    board2 = place_ship(board2, "cruiser", (2, 0), "h")
    board2 = place_ship(board2, "submarine", (7, 0), "h")
    board2 = place_ship(board2, "destroyer", (9, 0), "h")
    board1 = random_placement()
    state = new_game(board1, board2)
    state, _ = attack(state, "player1", (5, 3))
    state, _ = attack(state, "player2", (9, 9))
    state, _ = attack(state, "player1", (5, 4))
    state, _ = attack(state, "player2", (9, 8))
    coord = smart_strategy(state, "player1")
    assert coord in {(5, 2), (5, 5)}, f"Expected axis endpoint, got {coord}"


def test_smart_strategy_falls_through_when_all_target_candidates_attacked():
    from batalha_naval.board import place_ship, empty_board

    board2 = empty_board()
    board2 = place_ship(board2, "destroyer", (5, 5), "h")
    board2 = place_ship(board2, "carrier", (0, 0), "h")
    board2 = place_ship(board2, "battleship", (2, 0), "h")
    board2 = place_ship(board2, "cruiser", (4, 0), "h")
    board2 = place_ship(board2, "submarine", (7, 0), "h")
    board1 = random_placement()
    state = new_game(board1, board2)
    state, _ = attack(state, "player1", (5, 5))
    state, _ = attack(state, "player2", (9, 9))
    state, _ = attack(state, "player1", (4, 5))
    state, _ = attack(state, "player2", (9, 8))
    state, _ = attack(state, "player1", (6, 5))
    state, _ = attack(state, "player2", (9, 7))
    state, _ = attack(state, "player1", (5, 4))
    state, _ = attack(state, "player2", (9, 6))
    state, _ = attack(state, "player1", (5, 6))
    state, _ = attack(state, "player2", (9, 5))
    coord = smart_strategy(state, "player1")
    attacked = state["attacks"]["player1"]
    assert coord not in attacked
    r, c = coord
    assert 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

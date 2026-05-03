from batalha_naval.board import random_placement, BOARD_SIZE, place_ship, empty_board
from batalha_naval.game import new_game, attack, is_game_over, get_winner
from batalha_naval.loop import run_game
from batalha_naval.strategies import mcts_classic_strategy, random_strategy, Strategies


def test_mcts_classic_returns_valid_coord():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    coord = mcts_classic_strategy(state, "player1", time_budget=0.05)
    r, c = coord
    assert 0 <= r < BOARD_SIZE
    assert 0 <= c < BOARD_SIZE


def test_mcts_classic_does_not_return_attacked_coord():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    state, _ = attack(state, "player1", (0, 0))
    state, _ = attack(state, "player2", (9, 9))
    coord = mcts_classic_strategy(state, "player1", time_budget=0.05)
    assert coord not in state["attacks"]["player1"]


def test_mcts_classic_targets_adjacent_after_hit():
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
    coord = mcts_classic_strategy(state, "player1", time_budget=0.1)
    neighbors_of_hit = {(4, 5), (6, 5), (5, 4), (5, 6)}
    assert coord in neighbors_of_hit, f"Expected neighbor of hit, got {coord}"


def test_mcts_classic_continues_axis_after_two_hits():
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
    coord = mcts_classic_strategy(state, "player1", time_budget=0.1)
    assert coord in {(5, 2), (5, 5)}, f"Expected axis endpoint, got {coord}"


def test_smart_strategy_falls_through_when_all_target_candidates_attacked():
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
    coord = mcts_classic_strategy(state, "player1", time_budget=0.1)
    attacked = state["attacks"]["player1"]
    assert coord not in attacked
    r, c = coord
    assert 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def test_mcts_classic_simulates_full_game():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    strategies: Strategies = {
        "player1": lambda s, p: mcts_classic_strategy(s, p, time_budget=0.01),
        "player2": random_strategy,
    }
    final = run_game(state, strategies)
    assert is_game_over(final)
    assert get_winner(final) in {"player1", "player2"}

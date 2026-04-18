from batalha_naval.board import random_placement, SHIPS
from batalha_naval.game import new_game


def test_new_game_has_both_boards():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    assert state["boards"]["player1"] == board1
    assert state["boards"]["player2"] == board2


def test_new_game_player1_starts():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    assert state["current_turn"] == "player1"


def test_new_game_no_winner():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    assert state["winner"] is None


def test_new_game_no_attacks_yet():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    assert state["attacks"]["player1"] == frozenset()
    assert state["attacks"]["player2"] == frozenset()


def test_new_game_ships_have_all_cells():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    for player in ("player1", "player2"):
        for ship_name, size in SHIPS.items():
            assert len(state["ships"][player][ship_name]) == size

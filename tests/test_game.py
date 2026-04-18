from batalha_naval.board import random_placement, SHIPS, empty_board, place_ship
from batalha_naval.game import new_game, attack


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


def _game_with_known_boards():
    # player2 tem apenas um destroyer em (5,5) horizontal: células (5,5) e (5,6)
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    # player1 tem apenas um destroyer em (0,0) horizontal: células (0,0) e (0,1)
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    return new_game(board1, board2)


def test_attack_miss_returns_miss():
    state = _game_with_known_boards()
    new_state, result = attack(state, "player1", (0, 0))
    assert result == "miss"


def test_attack_miss_does_not_mutate():
    state = _game_with_known_boards()
    attack(state, "player1", (0, 0))
    assert state["attacks"]["player1"] == frozenset()


def test_attack_miss_records_coordinate():
    state = _game_with_known_boards()
    new_state, _ = attack(state, "player1", (0, 0))
    assert (0, 0) in new_state["attacks"]["player1"]


def test_attack_miss_switches_turn():
    state = _game_with_known_boards()
    new_state, _ = attack(state, "player1", (0, 0))
    assert new_state["current_turn"] == "player2"

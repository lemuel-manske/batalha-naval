from batalha_naval.board import random_placement, SHIPS, empty_board, place_ship
from batalha_naval.game import (
    new_game,
    attack,
    is_game_over,
    get_winner,
    is_valid_attack,
)


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
    _, result = attack(state, "player1", (0, 0))
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


def test_attack_hit_returns_hit():
    state = _game_with_known_boards()
    # destroyer do player2 está em (5,5) e (5,6)
    _, result = attack(state, "player1", (5, 5))
    assert result == "hit"


def test_attack_sunk_returns_sunk():
    state = _game_with_known_boards()
    state, _ = attack(state, "player1", (5, 5))
    # troca de turno — player2 ataca célula vazia
    state, _ = attack(state, "player2", (9, 9))
    # player1 afunda o destroyer
    state, result = attack(state, "player1", (5, 6))
    assert result == "sunk"


def test_attack_sunk_removes_ship_from_state():
    state = _game_with_known_boards()
    state, _ = attack(state, "player1", (5, 5))
    state, _ = attack(state, "player2", (9, 9))
    state, _ = attack(state, "player1", (5, 6))
    assert "destroyer" not in state["ships"]["player2"]


def test_game_not_over_at_start():
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    state = new_game(board1, board2)
    assert is_game_over(state) is False


def test_game_over_when_all_ships_sunk():
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    state = new_game(board1, board2)
    state, _ = attack(state, "player1", (5, 5))
    state, _ = attack(state, "player2", (9, 9))
    state, _ = attack(state, "player1", (5, 6))
    assert is_game_over(state) is True


def test_get_winner_none_at_start():
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    state = new_game(board1, board2)
    assert get_winner(state) is None


def test_get_winner_after_sinking_all():
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    state = new_game(board1, board2)
    state, _ = attack(state, "player1", (5, 5))
    state, _ = attack(state, "player2", (9, 9))
    state, _ = attack(state, "player1", (5, 6))
    assert get_winner(state) == "player1"


def test_valid_attack_on_fresh_game():
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    state = new_game(board1, board2)
    assert is_valid_attack(state, "player1", (0, 0)) is True


def test_invalid_attack_already_attacked():
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    state = new_game(board1, board2)
    state, _ = attack(state, "player1", (0, 0))
    state, _ = attack(state, "player2", (9, 9))
    assert is_valid_attack(state, "player1", (0, 0)) is False


def test_invalid_attack_out_of_bounds():
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    state = new_game(board1, board2)
    assert is_valid_attack(state, "player1", (10, 0)) is False
    assert is_valid_attack(state, "player1", (0, 10)) is False

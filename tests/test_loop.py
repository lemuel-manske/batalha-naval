from batalha_naval.board import empty_board, place_ship, random_placement
from batalha_naval.game import new_game, is_game_over, get_winner
from batalha_naval.loop import play_turn, run_game, Strategies
from batalha_naval.strategy import random_strategy


def _known_state():
    board1 = place_ship(empty_board(), "destroyer", (0, 0), "h")
    board2 = place_ship(empty_board(), "destroyer", (5, 5), "h")
    return new_game(board1, board2)


def test_play_turn_returns_new_state_and_result():
    state = _known_state()
    strategies: Strategies = {"player1": random_strategy, "player2": random_strategy}
    new_state, result = play_turn(state, strategies)
    assert result in ("miss", "hit", "sunk")
    assert new_state is not state


def test_play_turn_advances_turn():
    state = _known_state()
    strategies: Strategies = {"player1": random_strategy, "player2": random_strategy}
    new_state, _ = play_turn(state, strategies)
    assert new_state["current_turn"] == "player2"


def test_play_turn_does_not_mutate_state():
    state = _known_state()
    original_attacks = state["attacks"]["player1"]
    strategies: Strategies = {"player1": random_strategy, "player2": random_strategy}
    play_turn(state, strategies)
    assert state["attacks"]["player1"] == original_attacks


def test_run_game_ends_with_winner():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    strategies: Strategies = {"player1": random_strategy, "player2": random_strategy}
    final_state = run_game(state, strategies)
    assert is_game_over(final_state)
    assert get_winner(final_state) in ("player1", "player2")


def test_run_game_does_not_mutate_initial_state():
    board1 = random_placement()
    board2 = random_placement()
    state = new_game(board1, board2)
    original_attacks = state["attacks"]["player1"]
    strategies: Strategies = {"player1": random_strategy, "player2": random_strategy}
    run_game(state, strategies)
    assert state["attacks"]["player1"] == original_attacks

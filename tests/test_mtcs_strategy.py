from batalha_naval.board import random_placement, BOARD_SIZE
from batalha_naval.game import new_game, attack
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
    state, _ = attack(state, "player1", (0, 0))
    miss_coord2 = next(
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if (r, c) not in state["attacks"]["player2"]
    )
    state, _ = attack(state, "player2", miss_coord2)
    coord = mcts_strategy(state, "player1", time_budget=0.05)
    assert coord not in state["attacks"]["player1"]

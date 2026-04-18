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

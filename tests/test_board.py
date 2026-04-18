from batalha_naval.board import empty_board


def test_empty_board_has_10_rows():
    board = empty_board()
    assert len(board) == 10


def test_empty_board_has_10_columns():
    board = empty_board()
    assert all(len(row) == 10 for row in board)


def test_empty_board_all_cells_are_none():
    board = empty_board()
    assert all(cell is None for row in board for cell in row)

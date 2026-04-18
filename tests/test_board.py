from batalha_naval.board import empty_board, validate_placement


def test_empty_board_has_10_rows():
    board = empty_board()
    assert len(board) == 10


def test_empty_board_has_10_columns():
    board = empty_board()
    assert all(len(row) == 10 for row in board)


def test_empty_board_all_cells_are_none():
    board = empty_board()
    assert all(cell is None for row in board for cell in row)


def test_valid_placement_horizontal():
    board = empty_board()
    assert validate_placement(board, "destroyer", (0, 0), "h") is True


def test_valid_placement_vertical():
    board = empty_board()
    assert validate_placement(board, "destroyer", (0, 0), "v") is True


def test_placement_out_of_bounds_horizontal():
    board = empty_board()
    assert validate_placement(board, "destroyer", (0, 9), "h") is False


def test_placement_out_of_bounds_vertical():
    board = empty_board()
    assert validate_placement(board, "destroyer", (9, 0), "v") is False


def test_placement_overlaps_existing_ship():
    board = empty_board()
    occupied = tuple(
        tuple("destroyer" if (r, c) == (0, 0) else None for c in range(10))
        for r in range(10)
    )
    assert validate_placement(occupied, "destroyer", (0, 0), "h") is False

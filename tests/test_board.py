from batalha_naval.board import (
    empty_board,
    can_place_ship,
    place_ship,
    random_placement,
    SHIPS,
)


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
    assert can_place_ship(board, "destroyer", (0, 0), "h") is True


def test_valid_placement_vertical():
    board = empty_board()
    assert can_place_ship(board, "destroyer", (0, 0), "v") is True


def test_placement_out_of_bounds_horizontal():
    board = empty_board()
    assert can_place_ship(board, "destroyer", (0, 9), "h") is False


def test_placement_out_of_bounds_vertical():
    board = empty_board()
    assert can_place_ship(board, "destroyer", (9, 0), "v") is False


def test_placement_overlaps_existing_ship():
    occupied = tuple(
        tuple("destroyer" if (r, c) == (0, 0) else None for c in range(10))
        for r in range(10)
    )
    assert can_place_ship(occupied, "destroyer", (0, 0), "h") is False


def test_place_ship_fills_cells():
    board = empty_board()
    new_board = place_ship(board, "destroyer", (0, 0), "h")
    assert new_board[0][0] == "destroyer"
    assert new_board[0][1] == "destroyer"


def test_place_ship_does_not_mutate_original():
    board = empty_board()
    place_ship(board, "destroyer", (0, 0), "h")
    assert board[0][0] is None


def test_place_ship_vertical():
    board = empty_board()
    new_board = place_ship(board, "destroyer", (0, 0), "v")
    assert new_board[0][0] == "destroyer"
    assert new_board[1][0] == "destroyer"


def test_place_ship_invalid_raises():
    board = empty_board()
    try:
        place_ship(board, "destroyer", (0, 9), "h")
        assert False, "Should've raised ValueError"
    except ValueError:
        pass


def test_random_placement_places_all_ships():
    board = random_placement()
    placed = {
        board[r][c] for r in range(10) for c in range(10) if board[r][c] is not None
    }
    assert placed == set(SHIPS.keys())


def test_random_placement_correct_cell_count():
    board = random_placement()
    for ship_name, size in SHIPS.items():
        count = sum(1 for r in range(10) for c in range(10) if board[r][c] == ship_name)
        assert count == size


def test_random_placement_no_overlap():
    board = random_placement()
    cells = [
        board[r][c] for r in range(10) for c in range(10) if board[r][c] is not None
    ]
    assert len(cells) == sum(SHIPS.values())

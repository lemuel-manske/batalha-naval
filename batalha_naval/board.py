SHIPS = {
    "carrier": 5,
    "battleship": 4,
    "cruiser": 3,
    "submarine": 3,
    "destroyer": 2,
}


BOARD_SIZE = 10


def empty_board():
    return tuple(tuple(None for _ in range(BOARD_SIZE)) for _ in range(BOARD_SIZE))


def validate_placement(board, ship_name, start, direction):
    size = SHIPS[ship_name]
    row, col = start
    if direction == "h":
        cells = [(row, col + i) for i in range(size)]
    else:
        cells = [(row + i, col) for i in range(size)]
    if any(r > 9 or c > 9 for r, c in cells):
        return False
    return all(board[r][c] is None for r, c in cells)

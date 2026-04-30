import random

from typing import Literal

type Cell = str | None
type Row = tuple[Cell, ...]

type Board = tuple[Row, ...]

type Coord = tuple[int, int]
type Direction = Literal["h", "v"]  # horizontal ou vertical

type ShipName = str


SHIPS: dict[ShipName, int] = {
    "carrier": 5,
    "battleship": 4,
    "cruiser": 3,
    "submarine": 3,
    "destroyer": 2,
}

BOARD_SIZE = 10


def empty_board() -> Board:
    '''
    Checks if the board is empty, meaning all cells are `None`.
    '''

    return tuple(tuple(None for _ in range(BOARD_SIZE)) for _ in range(BOARD_SIZE))


def can_place_ship(
    board: Board,
    ship_name: ShipName,
    start: Coord,
    direction: Direction,
) -> bool:
    '''
    Validates if a ship can be placed on the board at the given starting coordinate and direction.
    '''

    size = SHIPS[ship_name]
    row, col = start

    if direction == "h":
        cells = [(row, col + i) for i in range(size)]
    else:
        cells = [(row + i, col) for i in range(size)]

    if any(r >= BOARD_SIZE or c >= BOARD_SIZE for r, c in cells):
        return False

    return all(board[r][c] is None for r, c in cells)


def place_ship(
    board: Board,
    ship_name: ShipName,
    start: Coord,
    direction: Direction,
) -> Board:
    '''
    Places a specified ship on the board at the given starting coordinate and direction, returning a new board with the ship placed.
    '''

    if not can_place_ship(board, ship_name, start, direction):
        raise ValueError(f"[place_ship] : invaliid {ship_name} in {start}, with direction {direction}")

    size = SHIPS[ship_name]
    row, col = start

    if direction == "h":
        cells = [(row, col + i) for i in range(size)]
    else:
        cells = [(row + i, col) for i in range(size)]

    rows = [list(r) for r in board]

    for r, c in cells:
        rows[r][c] = ship_name

    return tuple(tuple(r) for r in rows)


def random_placement() -> Board:
    '''
    Generates a random board configuration by placing all ships in random positions and orientations, ensuring that they do not overlap and fit within the board boundaries.
    '''

    board = empty_board()

    for ship_name in SHIPS:
        placed = False

        while not placed:
            direction: Direction = random.choice(["h", "v"])
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)

            if can_place_ship(board, ship_name, (row, col), direction):
                board = place_ship(board, ship_name, (row, col), direction)
                placed = True

    return board

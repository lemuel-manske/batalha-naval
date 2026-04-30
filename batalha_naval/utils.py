from batalha_naval.board import (
    BOARD_SIZE,
    Board,
    Coord,
    ShipName,
)

type ShipCells = frozenset[Coord]
type ShipMap = dict[ShipName, ShipCells]


def extract_ships(board: Board) -> ShipMap:
    '''
    Extracts the ships and their corresponding cells from the given board.
    '''

    ships: dict[ShipName, set[Coord]] = {}

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            name = board[r][c]
            if name is not None:
                ships.setdefault(name, set()).add((r, c))

    return {name: frozenset(cells) for name, cells in ships.items()}

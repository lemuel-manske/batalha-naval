from batalha_naval.board import Board, Coord, ShipName, BOARD_SIZE

type Player = str  # "player1" | "player2"

type ShipCells = frozenset[Coord]
type ShipMap = dict[ShipName, ShipCells]

type GameState = dict


def _extract_ships(board: Board) -> ShipMap:
    ships: dict[ShipName, set[Coord]] = {}

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            name = board[r][c]
            if name is not None:
                ships.setdefault(name, set()).add((r, c))

    return {name: frozenset(cells) for name, cells in ships.items()}


def new_game(board1: Board, board2: Board) -> GameState:
    return {
        "boards": {
            "player1": board1,
            "player2": board2,
        },
        "ships": {
            "player1": _extract_ships(board1),
            "player2": _extract_ships(board2),
        },
        "attacks": {
            "player1": frozenset(),
            "player2": frozenset(),
        },
        "current_turn": "player1",
        "winner": None,
    }

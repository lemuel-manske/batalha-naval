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

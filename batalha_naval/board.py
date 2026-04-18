SHIPS = {
    "carrier": 5,
    "battleship": 4,
    "cruiser": 3,
    "submarine": 3,
    "destroyer": 2,
}


def empty_board():
    return tuple(tuple(None for _ in range(10)) for _ in range(10))
